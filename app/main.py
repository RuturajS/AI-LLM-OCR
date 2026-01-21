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
    model: str = Form(None)
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
        
        if not final_api_key:
            return JSONResponse(status_code=400, content={"error": f"No API Key provided for {provider}"})

        # Process
        result_text = engine.extract(provider, contents, prompt, final_api_key, model)
        
        # Save to history
        entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "filename": file.filename,
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
    return {"message": "History cleared"}

# Serve Frontend
# We will mount static files. 
# Ensure the directory exists to avoid errors on startup if user acts fast.
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
