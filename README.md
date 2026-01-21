# AI Smart OCR 🚀

> A powerful, accessible AI-powered OCR tool using OpenAI and Gemini Vision APIs. No local model installation needed!

## Features ✅

- **Choice of Provider**: OpenAI (GPT-4o), Google Gemini, or Local (EasyOCR/Tesseract).
- **Context-Aware**: Ask specifically for tables, forms, or data extraction.
- **Web Interface**: Clean, dark-mode UI with drag-and-drop.
- **CLI Support**: Automate workflows via command line.
- **Privacy-First**: Local OCR options available.

## Quick Start

### Prerequisites
- **Node.js** (v14+)
- **Python** (3.9+)
- API Key from [OpenAI](https://platform.openai.com) or [Google Gemini](https://aistudio.google.com) (Optional if using local OCR).

### Installation

1. **Clone & Install Dependencies**
   ```bash
   git clone https://github.com/RuturajS/AI-LLM-OCR.git
   cd AI-LLM-OCR
   
   # Install Web Backend Dependencies
   npm install
   
   # Install Python Worker Dependencies (for Local OCR & CLI)
   pip install -r requirements.txt
   ```

2. **Setup Environment**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=sk-...
   GEMINI_API_KEY=AIza...
   ```

### Usage

#### 1. Web Interface 🌐
Run the web server:
```bash
npm start
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

#### 2. CLI Tool 💻
Extract text directly from your terminal:
```bash
# Basic Extraction
python cli.py extract image.png

# Custom Prompt with Gemini
python cli.py extract invoice.pdf --provider gemini --prompt "Extract total amount"
```

### Local OCR Options (No API Costs)

#### 1. EasyOCR (Recommended for Local)
Select "EasyOCR" in the dropdown. It runs entirely on your CPU/GPU using Python. **No extra installation needed** for images.

**For PDF Support (Windows Only):**
You must install **Poppler** to process PDFs locally:
1. Download the latest release from [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/).
2. Extract the zip file (e.g., to `C:\Program Files\Poppler`).
3. Add the `bin` folder to your System PATH or create a `.env` variable:
   ```env
   POPPLER_PATH=C:\Program Files\Poppler\Library\bin
   ```

## Contributing 🤝
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---
**Maintained by**: Ruturaj