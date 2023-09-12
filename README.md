# 📖 Laboratorio de Manipulación de Libros en PDF con Python

Este repositorio contiene un **laboratorio básico de manipulación de datos con Python** aplicado a la transformación de libros en formato PDF.

La idea principal es experimentar con **cómo dividir páginas de un libro** para obtener diferentes perspectivas:

- **De más a menos páginas:**  
  Un mismo libro puede representarse en diferentes formas:  
  - **1 página original → múltiples páginas de salida.**  
  - **Múltiples páginas → se reconstruyen como una.**  
  - **Hasta volver a la forma original (1:1).**

En otras palabras:  
👉 *"De una página hacer más de una, y finalmente volver a una sola."*

---

## 🎯 Objetivos

- Explorar la manipulación de PDFs con **Python**.  
- Experimentar con **división de páginas** (ej. cortar una página en dos mitades verticales).  
- Aplicar **OCR en español** para recuperar texto seleccionable de libros escaneados.  
- Estandarizar el texto a una fuente legible (**Arial**).  
- Mejorar la legibilidad mediante **corrección ortográfica en castellano**.  
- Documentar el proceso como un **laboratorio educativo de datos**.

---

## 🛠️ Tecnologías y librerías usadas

- [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) → para leer y renderizar PDFs.  
- [Pillow](https://pillow.readthedocs.io/) → para manejar imágenes.  
- [pytesseract](https://pypi.org/project/pytesseract/) → OCR con Tesseract.  
- [ReportLab](https://www.reportlab.com/dev/docs/) → para reconstruir PDFs con texto.  
- [language-tool-python](https://pypi.org/project/language-tool-python/) → corrección ortográfica/gramatical en español.  
- [pyspellchecker](https://pypi.org/project/pyspellchecker/) → corrector básico (fallback si no está LanguageTool).  

---

## 📂 Estructura del proyecto

```
.
├── pdf_vertical_ocr_arial.py   # Script principal para dividir páginas y reconstruir PDF
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Este archivo
```

---

## ⚙️ Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tuusuario/laboratorio-pdf.git
cd laboratorio-pdf
```

2. Crear entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Instalar **Tesseract OCR** en tu sistema:

- Linux: `sudo apt-get install tesseract-ocr tesseract-ocr-spa`  
- macOS: `brew install tesseract`  
- Windows: [instalador oficial](https://github.com/UB-Mannheim/tesseract/wiki)  

---

## 🚀 Uso

Ejemplo básico:

```bash
python pdf_vertical_ocr_arial.py --input "libro_original.pdf" --output "libro_dividido.pdf" --dpi 300
```

- Omite la primera página por defecto.  
- Si quieres conservarla, usa `--keep-first`.

---

## 🧪 Qué aprenderás en este laboratorio

- Cómo leer y manipular PDFs en Python.  
- Cómo cortar páginas en mitades **verticales u horizontales**.  
- Cómo aplicar **OCR en español** para recuperar texto editable.  
- Cómo reconstruir PDFs con **texto seleccionable en Arial**.  
- Cómo integrar **corrección ortográfica automática** en castellano.  

---

## 🌟 Ejemplos de experimentación

1. **De 1 página → 2 páginas:**  
   - Cortamos cada página en 2 mitades (verticales u horizontales).  

2. **De varias páginas → 1:**  
   - Reconstruimos texto continuo a partir de múltiples páginas.  

3. **De nuevo a 1:1:**  
   - Recuperamos la forma original tras experimentos de expansión.  

Esto nos permite ver un flujo completo de **transformación y restauración de datos**.

---

## 🔄 Diagrama del flujo de transformación

```text
 ┌──────────┐
 │ 1 página │
 └────┬─────┘
      │ dividir (OCR + Arial)
      ▼
 ┌─────────────┐
 │ varias pzas │  (mitades izquierda / derecha)
 └────┬────────┘
      │ recomponer (texto corregido)
      ▼
 ┌──────────┐
 │ 1 página │
 └──────────┘
```

---

## 📌 Conclusiones

Este proyecto sirve como **laboratorio de prácticas** para:

- Estudiantes que quieran aprender a manipular datos con Python.  
- Personas interesadas en el procesamiento de documentos.  
- Cualquier curioso que desee experimentar con OCR y corrección de texto en español.  

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.  
