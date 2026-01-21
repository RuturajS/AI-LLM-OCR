import sys
import os
import json
import base64
from io import BytesIO

# Suppress logs
import logging
logging.getLogger('easyocr').setLevel(logging.ERROR)

def process_tesseract(file_path):
    try:
        import pytesseract
        from PIL import Image
        
        # Windows Path Check
        if os.name == 'nt':
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\rutur\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            env_path = os.getenv("TESSERACT_PATH")
            if env_path and os.path.exists(env_path):
                 pytesseract.pytesseract.tesseract_cmd = env_path
            else:
                import shutil
                if not shutil.which("tesseract"):
                    for p in common_paths:
                        if os.path.exists(p):
                            pytesseract.pytesseract.tesseract_cmd = p
                            break
                            
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text if text.strip() else "No text found."
    except Exception as e:
        return f"Tesseract Error: {str(e)}"

def process_easyocr(file_path):
    try:
        import easyocr
        import numpy as np
        from PIL import Image
        # PDF support
        try:
            from pdf2image import convert_from_path
        except:
            pass

        reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        
        # Check PDF
        if file_path.lower().endswith('.pdf'):
            try:
                # Check for explicit Poppler path in env
                poppler_path_env = os.getenv("POPPLER_PATH")
                kwargs = {}
                if poppler_path_env and os.path.exists(poppler_path_env):
                    kwargs['poppler_path'] = poppler_path_env

                # Convert PDF to images
                images = convert_from_path(file_path, **kwargs)
                
                full_text = []
                for i, img in enumerate(images):
                    img_np = np.array(img)
                    results = reader.readtext(img_np)
                    page_text = "\n".join([res[1] for res in results])
                    full_text.append(f"--- Page {i+1} ---\n{page_text}")
                return "\n\n".join(full_text)
            except Exception as e:
                err_msg = str(e).lower()
                if "poppler" in err_msg or "page count" in err_msg:
                    return (
                        "PDF Error: Poppler is required for PDF processing with EasyOCR.\n"
                        "1. Download Poppler for Windows (e.g., from https://github.com/oschwartz10612/poppler-windows/releases/)\n"
                        "2. Extract it and set 'POPPLER_PATH' in your .env file to the 'bin' folder (e.g., C:\\...\\poppler-xx\\bin)\n"
                        "3. Or add it to your system PATH."
                    )
                return f"PDF Error: {str(e)}"
        
        # Image
        results = reader.readtext(file_path)
        return "\n".join([res[1] for res in results])
    except Exception as e:
        return f"EasyOCR Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python_worker.py <provider> <file_path>")
        sys.exit(1)
        
    provider = sys.argv[1]
    file_path = sys.argv[2]
    
    if provider == "tesseract":
        print(process_tesseract(file_path))
    elif provider == "easyocr":
        print(process_easyocr(file_path))
    else:
        print("Unknown provider")
