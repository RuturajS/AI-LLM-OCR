import os
import base64
import json
from io import BytesIO
from google import genai
from google.genai import types
from openai import OpenAI
from typing import Optional, List, Dict, Union
import shutil
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

# Global lazy load for easyocr to avoid startup overhead
easyocr_reader = None

class OCREngine:
    def __init__(self):
        pass

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode('utf-8')

    def process_openai(self, image_bytes: bytes, prompt: str, api_key: str, model: str = "gpt-4o", **kwargs) -> str:
        client = OpenAI(api_key=api_key)
        base64_image = self._encode_image(image_bytes)
        
        # Parse kwargs
        max_tokens = int(kwargs.get("max_tokens", 4096))
        temperature = float(kwargs.get("temperature", 0.0))
        system_prompt = kwargs.get("system_prompt", "You are an AI assistant that extracts text from images.")
        
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def process_gemini(self, image_bytes: bytes, prompt: str, api_key: str, model: str = "gemini-1.5-flash", **kwargs) -> str:
        client = genai.Client(api_key=api_key)
        
        try:
           from PIL import Image
           p_img = Image.open(BytesIO(image_bytes))
        except Exception as e:
            return f"Error processing image for Gemini: {str(e)}"

        # List of models to try in order of preference
        # If the user provided a specific model, try that first.
        # Then fall back to known working models.
        models_to_try = []
        if model:
            models_to_try.append(model)
        
        # Add fallbacks if they aren't already in the list
        fallbacks = ["gemini-1.5-flash", "gemini-1.5-flash-001", "gemini-1.5-pro", "gemini-pro-vision"]
        for m in fallbacks:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        
        for m_name in models_to_try:
            try:
                # print(f"Trying model: {m_name}") # Debugging
                response = client.models.generate_content(
                    model=m_name,
                    contents=[prompt, p_img]
                )
                return response.text
            except Exception as e:
                last_error = str(e)
                # If it's a 404 (Not Found), try the next model.
                # If it's a 401 (Auth) or 429 (Quota), failing fast is usually better, 
                # but for simplicity we'll try the next just in case permissions differ.
                if "404" in last_error or "not found" in last_error.lower():
                    continue
                else:
                    # Non-404 error (e.g. Auth), probably fatal. Stop trying.
                    return f"Gemini API Error with model '{m_name}': {last_error}"
        
        return f"Error: Could not generate content with any tried models ({models_to_try}). Last error: {last_error}"

    def process_openrouter(self, image_bytes: bytes, prompt: str, api_key: str, model: str = "google/gemini-pro-vision", **kwargs) -> str:
        # Debug: Print first few chars of key to ensure it isn't empty/weird
        print(f"OpenRouter Debug: Key='{api_key[:5]}...' len={len(api_key)}")
        
        # Parse kwargs
        max_tokens = int(kwargs.get("max_tokens", 4096))
        temperature = float(kwargs.get("temperature", 0.0))
        system_prompt = kwargs.get("system_prompt", "You are an AI assistant that extracts text from images.")

        # OpenRouter uses OpenAI-compatible API
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip(),
        )
        base64_image = self._encode_image(image_bytes)
        
        # OpenRouter requires specific site headers usually, but we'll try minimal first
        extra_headers = {
            "HTTP-Referer": "https://github.com/RuturajS/AI-LLM-OCR", 
            "X-Title": "AI-LLM-OCR"
        }
        
        response = client.chat.completions.create(
            model=model,
            extra_headers=extra_headers,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def process_tesseract(self, image_bytes: bytes) -> str:
        if not pytesseract:
            return "Error: pytesseract is not installed. Please install it via 'pip install pytesseract'."
            
        # Helper to check common Windows paths if not in PATH
        if os.name == 'nt':
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\rutur\AppData\Local\Tesseract-OCR\tesseract.exe"
            ]
            # Check if tesseract is configured in Env
            env_path = os.getenv("TESSERACT_PATH")
            if env_path and os.path.exists(env_path):
                 pytesseract.pytesseract.tesseract_cmd = env_path
            
            # Check if tesseract is already in path
            elif not shutil.which("tesseract"):
                for p in common_paths:
                    if os.path.exists(p):
                        pytesseract.pytesseract.tesseract_cmd = p
                        break
            
        try:
            img = Image.open(BytesIO(image_bytes))
            # Basic extraction, no prompt control for Tesseract as it is traditional OCR
            text = pytesseract.image_to_string(img)
            return text if text.strip() else "No text found by Tesseract."
        except Exception as e:
            if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
                 return "Error: Tesseract binary not found. Please download and install it from https://github.com/UB-Mannheim/tesseract/wiki (Windows) or install via brew/apt."
            return f"Error processing with Tesseract: {str(e)}"

    def process_easyocr(self, image_bytes: bytes) -> str:
        # EasyOCR runs in python, no external exe (besides what pip installed)
        # It handles torch download.
        global easyocr_reader
        try:
            import easyocr
            import numpy as np
        except ImportError:
            return "Error: easyocr module not found. Please pip install easyocr."
            
        try:
            if easyocr_reader is None:
                # Initialize for English by default. CPU is default unless gpu=True
                # Using gpu=False for better compatibility if user lacks CUDA setup
                easyocr_reader = easyocr.Reader(['en'], gpu=False)
                
            img = Image.open(BytesIO(image_bytes))
            # Convert to numpy array
            img_np = np.array(img)
            
            # EasyOCR returns list of (bbox, text, conf)
            results = easyocr_reader.readtext(img_np)
            
            # Join text
            text_out = "\n".join([res[1] for res in results])
            return text_out if text_out.strip() else "No text found by EasyOCR."
            
        except Exception as e:
            return f"Error with EasyOCR: {str(e)}"

    def extract(self, provider: str, image_bytes: bytes, prompt: str, api_key: str, model: Optional[str] = None, **kwargs) -> Union[str, Dict]:
        try:
            if provider.lower() == "openai":
                return self.process_openai(image_bytes, prompt, api_key, model or "gpt-4o", **kwargs)
            elif provider.lower() == "gemini":
                # Gemini support logic can be complex for system prompts, skipping deep kwargs for now
                return self.process_gemini(image_bytes, prompt, api_key, model or "gemini-1.5-flash-001", **kwargs)
            elif provider.lower() == "openrouter":
                # Use a reliable free model as default, e.g. Llama 3.2 Vision
                return self.process_openrouter(image_bytes, prompt, api_key, model or "meta-llama/llama-3.2-11b-vision-instruct:free", **kwargs)
            elif provider.lower() == "tesseract":
                return self.process_tesseract(image_bytes)
            elif provider.lower() == "easyocr":
                return self.process_easyocr(image_bytes)
            else:
                raise ValueError(f"Invalid provider: {provider}")
        except Exception as e:
            return f"Error: {str(e)}"
