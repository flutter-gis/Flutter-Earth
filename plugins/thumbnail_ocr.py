# Plugin: thumbnail_ocr.py
# This plugin extracts text from thumbnail images using OCR (pytesseract).

from PIL import Image
import pytesseract

def extract_text_from_thumbnail(image_path):
    """
    Extracts text from a thumbnail image using OCR.
    Returns the extracted text as a string.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"[OCR ERROR] {e}" 