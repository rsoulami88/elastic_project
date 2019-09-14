import os
import slate3k as slate
import json
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def read_pdf(filepath):
    with open(filepath, 'rb') as f:
        text = str(slate.PDF(f))
        text = text.replace('\\n',' ')
        text = text.replace('\\t',' ')
        text = text.replace('\\r',' ')
    return text

def pdf_image_to_text(filepath):
    images = convert_from_path(filepath)
    pages = []
    for i in range(len(images)):
        pages.append(pytesseract.image_to_string(images[i]))
    text = '/n'.join(pages)
    text = text.replace('\\n',' ')
    text = text.replace('\\t',' ')
    text = text.replace('\\r',' ')
    return text