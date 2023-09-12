#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_vertical_ocr_arial.py

Pipeline: "1 página -> 2 mitades (izq/der) -> OCR por mitad -> normalización + corrección -> PDF nuevo con texto seleccionable".
Se omite la primera página por defecto (habitual en libros escaneados con portada).

Diseño para clases linealmente independientes (futuras):
  - PDFLoader        (carga)
  - PageSplitter     (corte vertical/horizontal)
  - OCRProcessor     (pytesseract + idioma 'spa')
  - TextNormalizer   (limpieza post-OCR: guiones, saltos, espacios)
  - SpellCorrector   (LanguageTool o SpellChecker)
  - PDFWriter        (ReportLab: fuente Arial/alternativa y envoltura de líneas)
En este archivo concentramos el flujo en una sola clase "VerticalPDFProcessor", pero cada
bloque está encapsulado en funciones bien delimitadas para poder extraerlas a clases.
"""

import os, io, sys, argparse
import fitz                           # PyMuPDF: lectura/render PDF
from PIL import Image                 # Pillow: manejo de imágenes
import pytesseract                    # OCR

# ------------------ Corrección ortográfica ------------------
USE_LT = True
lt_tool = None
spell = None

def setup_spell_tools():
    """
    Inicializa la herramienta de corrección:
      - Intenta LanguageTool (mejor gramática/acentos).
      - Si falla, cae a pyspellchecker (básico).
      - Si tampoco está, se omite la corrección.
    """
    global lt_tool, spell, USE_LT
    try:
        import language_tool_python
        lt_tool = language_tool_python.LanguageTool('es')
        USE_LT = True
        print("[INFO] LanguageTool disponible para corrección en español.")
    except Exception as e:
        print(f"[AVISO] LanguageTool no disponible ({e}). Uso alternativo con pyspellchecker.")
        USE_LT = False
        try:
            from spellchecker import SpellChecker
            spell = SpellChecker(language="es")
        except Exception as e2:
            print(f"[AVISO] pyspellchecker tampoco disponible ({e2}). Se omitirá la corrección ortográfica.")

def correct_spanish_text(text: str) -> str:
    """
    Limpia ruido típico de OCR y corrige español con LT o SpellChecker cuando haya.
    """
    if not text or text.strip() == "":
        return text

    import re
    # --- Normalización rápida post-OCR ---
    text = re.sub(r"-\n", "", text)         # une palabras cortadas por guion al salto
    text = re.sub(r"[ \t]+\n", "\n", text)  # elimina espacios antes de salto
    text = re.sub(r"\n{3,}", "\n\n", text)  # comprime saltos múltiples
    text = re.sub(r"[ ]{2,}", " ", text)    # comprime espacios

    # --- Corrección con LanguageTool (si está disponible) ---
    try:
        if lt_tool is not None:
            import language_tool_python
            matches = lt_tool.check(text)
            return language_tool_python.utils.correct(text, matches)
    except Exception:
        pass  # cae al siguiente método

    # --- Corrección con SpellChecker (básica, palabra a palabra) ---
    if spell is not None:
        tokens = []
        for tok in text.split():
            if any(ch.isalpha() for ch in tok):
                # conserva puntuación contigua
                prefix, suffix, core = "", "", tok
                while core and not core[0].isalnum():
                    prefix += core[0]; core = core[1:]
                while core and not core[-1].isalnum():
                    suffix = core[-1] + suffix; core = core[:-1]
                if core:
                    suggestion = spell.correction(core)
                    if suggestion:
                        tok = prefix + suggestion + suffix
            tokens.append(tok)
        return " ".join(tokens)

    # --- Sin correctores disponibles ---
    return text

# ------------------ Escritura PDF (ReportLab) ------------------
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.utils import simpleSplit

def pick_font():
    """
    Intenta registrar Arial. Si no existe, usa DejaVuSans/FreeSans.
    Si ninguna está, recurre a Helvetica (fuente base).
    """
    candidates = [
        ("Arial", "Arial.ttf"),
        ("Arial", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"),
        ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("FreeSans", "/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
    ]
    for reg_name, path in candidates:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(reg_name, path))
                print(f"[INFO] Fuente registrada: {reg_name} ({path})")
                return reg_name
        except Exception:
            continue
    print("[AVISO] No se encontró Arial/DejaVu/FreeSans. Se usará Helvetica del sistema.")
    return "Helvetica"

def write_wrapped_page(text, canv, font_name="Helvetica", font_size=11, margins=(50,50,50,50)):
    """
    Dibuja 'text' en una página A4 con ajuste de líneas (word wrap) y márgenes.
    Siempre cierra la página (showPage) al final.
    """
    left, right, top, bottom = margins
    page_w, page_h = A4
    usable_w = page_w - left - right
    line_h = font_size * 1.27

    canv.setFont(font_name, font_size)
    y = page_h - top

    if not text or not text.strip():
        canv.showPage()
        return

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        # Mantener una sola línea en blanco como máximo
        if line.strip() == "":
            y -= line_h
            if y < bottom:
                canv.showPage(); canv.setFont(font_name, font_size); y = page_h - top
            continue

        # Divide la línea larga en segmentos que quepan en el ancho útil
        for w_line in simpleSplit(line, font_name, font_size, usable_w):
            canv.drawString(left, y, w_line)
            y -= line_h
            if y < bottom:
                canv.showPage(); canv.setFont(font_name, font_size); y = page_h - top

    canv.showPage()

# ------------------ OCR por mitad ------------------
def ocr_half_pixmap(pixmap, lang="spa"):
    """
    Convierte un fitz.Pixmap a PNG en memoria, lo abre con PIL y ejecuta pytesseract.
    """
    img_bytes = pixmap.tobytes("png")
    pil_img = Image.open(io.BytesIO(img_bytes))
    return pytesseract.image_to_string(pil_img, lang=lang)

# ------------------ Procesador principal ------------------
class VerticalPDFProcessor:
    """
    Encapsula el pipeline vertical: split -> OCR -> corrección -> escritura PDF.
    """
    def __init__(self, dpi=300, omit_first=True):
        self.dpi = dpi
        self.omit_first = omit_first
        setup_spell_tools()
        self.font_name = pick_font()

    def process(self, input_path: str, output_path: str):
        # 1) Cargar PDF
        doc = fitz.open(input_path)
        # 2) Preparar PDF de salida
        canv = canvas.Canvas(output_path, pagesize=A4)

        # 3) Determinar desde qué página empezar (omitir portada)
        start_page = 1 if self.omit_first else 0
        total_in = len(doc) - start_page
        print(f"[INFO] Páginas de entrada: {len(doc)} | Omitir primera: {self.omit_first} | A procesar: {max(0,total_in)}")

        # 4) Iterar páginas, dividir verticalmente y OCR por mitad
        m = fitz.Matrix(self.dpi/72, self.dpi/72)  # escalado para DPI deseados
        for i in range(start_page, len(doc)):
            page = doc[i]
            rect = page.rect
            mid_x = rect.width / 2.0

            # Rectángulos de recorte (izquierda / derecha)
            left_clip  = fitz.Rect(0,      0, mid_x,       rect.height)
            right_clip = fitz.Rect(mid_x,  0, rect.width,  rect.height)

            # Render a pixmap (bitmap) por mitad
            left_pix  = page.get_pixmap(matrix=m, clip=left_clip,  alpha=False)
            right_pix = page.get_pixmap(matrix=m, clip=right_clip, alpha=False)

            # OCR español por mitades (mantiene la concordancia de párrafos por columna)
            left_text  = correct_spanish_text(ocr_half_pixmap(left_pix,  lang="spa"))
            right_text = correct_spanish_text(ocr_half_pixmap(right_pix, lang="spa"))

            # 5) Escribir cada mitad como página nueva con fuente legible
            write_wrapped_page(left_text,  canv, font_name=self.font_name, font_size=11)
            write_wrapped_page(right_text, canv, font_name=self.font_name, font_size=11)

            print(f"[OK] Página {i+1}/{len(doc)} -> 2 páginas de salida")

        # 6) Guardar PDF final
        canv.save()
        print(f"[LISTO] PDF generado: {output_path}")

# ------------------ CLI ------------------
def build_arg_parser():
    ap = argparse.ArgumentParser(
        description="Divide verticalmente cada página, hace OCR en español por mitades y recompone un PDF con texto seleccionable (Arial/alternativa)."
    )
    ap.add_argument("--input", "-i", required=True, help="Ruta del PDF de entrada")
    ap.add_argument("--output", "-o", required=True, help="Ruta del PDF de salida")
    ap.add_argument("--dpi", type=int, default=300, help="Resolución de rasterizado para OCR (recomendado 300)")
    ap.add_argument("--keep-first", action="store_true", help="No omitir la primera página")
    return ap

def main():
    args = build_arg_parser().parse_args()
    if not os.path.exists(args.input):
        print(f"ERROR: No existe el archivo de entrada: {args.input}", file=sys.stderr)
        sys.exit(1)

    # Instanciar y ejecutar la CLASE sobre el archivo
    processor = VerticalPDFProcessor(dpi=args.dpi, omit_first=(not args.keep_first))
    processor.process(args.input, args.output)

if __name__ == "__main__":
    main()
