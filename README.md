# AI Smart OCR 🚀

> A powerful, accessible AI-powered OCR tool using OpenAI and Gemini Vision APIs. No local model installation needed!

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-green)

## Project Concept
**Smart OCR with AI Context Extraction**  
A web-based and CLI tool for extracting structured data from images and PDFs using state-of-the-art multimodal LLMs. Perfect for QA testers, data entry automation, and verifying UI elements.

## Features ✅

- **No Local Installation**: Powered by Cloud APIs (OpenAI & Google Gemini).
- **Context-Aware**: Ask specifically for tables, forms, or specific text fields.
- **Web Interface**: Modern, dark-mode UI with drag-and-drop.
- **Multi-Format**: Supports PNG, JPG, PDF.
- **CLI Support**: Automate workflows via command line.
- **History**: Tracks past extractions.
- **Dockerized**: easy deployment.

## Quick Start

### Prerequisites
- Python 3.9+ OR Docker
- API Key from [OpenAI](https://platform.openai.com) or [Google Gemini](https://aistudio.google.com).

### Running Locally (Python)

1. **Clone & Install**
   ```bash
   git clone https://github.com/RuturajS/AI-LLM-OCR.git
   cd AI-LLM-OCR
   pip install -r requirements.txt
   ```

2. **Run Server**
   ```bash
   uvicorn backend.main:app --reload
   ```
   Open [http://localhost:8000](http://localhost:8000) in your browser.

### Running with Docker 🐳

```bash
docker build -t ai-smart-ocr .
docker run -p 8000:8000 --env OPENAI_API_KEY=your_key ai-smart-ocr
```

### CLI Usage 💻

Extract text directly from your terminal:

```bash
# Basic Extraction
python cli.py extract image.png

# Custom Prompt
python cli.py extract invoice.pdf --prompt "Extract total amount and date as JSON"

# Use Gemini
python cli.py extract screenshot.png --provider gemini --key "AIza..."

# View History
python cli.py history
```

## Configuration

You can set API keys in the Web UI settings or via environment variables:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY`

## Use Cases 💡

1. **QA Testing**: Validate error messages in screenshots.
   *Prompt: "Extract all error messages and their color codes."*
   
2. **Data Entry**: Convert invoice photos to JSON.
   *Prompt: "Extract vendor, date, and total amount in JSON format."*
   
3. **Accessibility**: Get image descriptions.
   *Prompt: "Describe the UI layout for a screen reader."*

## Contributing 🤝

We welcome contributions! Please follow these rules:

1. **Fork the repo** and create a concise branch name.
2. **Code Style**: Ensure Python code is typed and formatted.
3. **Commit Messages**: Use conventional commits (e.g., `feat: add new provider`).
4. **Pull Request**: Describe your changes clearly.

### Tags
#OCR #AI #OpenAI #Gemini #Python #FastAPI #Docker #Automation

---
**Maintainer**: Ruturaj