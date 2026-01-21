import os
import base64
import json
from io import BytesIO
from google import genai
from google.genai import types
from openai import OpenAI
from typing import Optional, List, Dict, Union

class OCREngine:
    def __init__(self):
        pass

    def _encode_image(self, image_bytes: bytes) -> str:
        return base64.b64encode(image_bytes).decode('utf-8')

    def process_openai(self, image_bytes: bytes, prompt: str, api_key: str, model: str = "gpt-4o") -> str:
        client = OpenAI(api_key=api_key)
        base64_image = self._encode_image(image_bytes)
        
        response = client.chat.completions.create(
            model=model,
            messages=[
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
            max_tokens=4096,
        )
        return response.choices[0].message.content

    def process_gemini(self, image_bytes: bytes, prompt: str, api_key: str, model: str = "gemini-1.5-flash-001") -> str:
        client = genai.Client(api_key=api_key)
        
        # Open image using PIL to ensure format compatibility if needed, 
        # or pass bytes directly if supported. The new SDK supports PIL images well.
        try:
           from PIL import Image
           p_img = Image.open(BytesIO(image_bytes))
        except Exception as e:
            return f"Error processing image for Gemini: {str(e)}"

        try:
            response = client.models.generate_content(
                model=model,
                contents=[prompt, p_img]
            )
            return response.text
        except Exception as e:
            # Check for common model/key errors
            err_str = str(e)
            if "404" in err_str and "not found" in err_str:
                return f"Error: Model '{model}' not found or not available with this API key/version. Try using 'gemini-1.5-flash-001' or check your API key permissions. Original error: {err_str}"
            return f"Gemini API Error: {err_str}"

    def extract(self, provider: str, image_bytes: bytes, prompt: str, api_key: str, model: Optional[str] = None) -> Union[str, Dict]:
        try:
            if provider.lower() == "openai":
                return self.process_openai(image_bytes, prompt, api_key, model or "gpt-4o")
            elif provider.lower() == "gemini":
                return self.process_gemini(image_bytes, prompt, api_key, model or "gemini-1.5-flash-001")
            else:
                raise ValueError("Invalid provider using 'openai' or 'gemini'")
        except Exception as e:
            return f"Error: {str(e)}"
