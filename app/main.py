from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import shutil
import os
import json
import uuid
from datetime import datetime
from app.ocr_engine import OCREngine

app = FastAPI(title="AI-LLM-OCR", description="Smart OCR with AI Context Extraction")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Engine
engine = OCREngine()

# History Storage
HISTORY_FILE = "history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(entry):
    history = load_history()
    history.insert(0, entry) # Prepend
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

class ExtractRequest(BaseModel):
    prompt: str
    provider: str
    api_key: Optional[str] = None

@app.post("/api/extract")
async def extract_text(
    file: UploadFile = File(...),
    prompt: str = Form("Extract everything"),
    provider: str = Form("openai"),
    api_key: str = Form(None),
    model: str = Form(None),
    max_tokens: int = Form(4096),
    temperature: float = Form(0.0),
    system_prompt: str = Form(None)
):
    try:
        contents = await file.read()
        
        # Determine API Key
        final_api_key = api_key
        if not final_api_key:
            if provider == "openai":
                final_api_key = os.getenv("OPENAI_API_KEY")
            elif provider == "gemini":
                final_api_key = os.getenv("GEMINI_API_KEY")
            elif provider == "openrouter":
                final_api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Validation: Tesseract does not need a key
        if not final_api_key and provider != "tesseract" and provider != "easyocr":
            return JSONResponse(status_code=400, content={"error": f"No API Key provided for {provider}"})

        # Process
        result_text = engine.extract(
            provider, 
            contents, 
            prompt, 
            final_api_key, 
            model,
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=system_prompt or "You are an AI assistant that extracts text from images."
        )
        
        # Save image to uploads directory
        if not os.path.exists("uploads"):
            os.makedirs("uploads")
            
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join("uploads", unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Save to history
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
            "image_path": f"/uploads/{unique_filename}",
            "provider": provider,
            "prompt": prompt,
            "result": result_text
        }
        save_history(entry)
        
        return entry
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/history")
async def get_history():
    return load_history()

@app.delete("/api/history")
async def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    # Also clean uploads if desired, but for now just history
    return {"message": "History cleared"}

# Serve Frontend
# We will mount static files. 
# Ensure the directory exists to avoid errors on startup if user acts fast.
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
