# Contributing to AI-LLM-OCR 🚀

First off, thank you for considering contributing to AI-LLM-OCR! It's people like you that make this tool faster, safer, and more easier to use. 

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

## 🛠️ Getting Started

### Prerequisites
- Python 3.9+
- Git
- Access to OpenAI or Google Gemini API keys for testing.

### Local Development Setup

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/AI-LLM-OCR.git
   cd AI-LLM-OCR
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Set up Environment Variables**:
   Create a `.env` file in the root directory (do not commit this file!):
   ```env
   OPENAI_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   ```

### Running the App
- **Web Server**: `uvicorn app.main:app --reload`
- **CLI Tool**: `python cli.py --help`

---

## 💻 contributing Code

### Project Structure
- `app/`: Core backend logic (FastAPI, OCR Engine).
- `static/`: Frontend assets (HTML, CSS, JS).
- `cli.py`: Command-line interface logic.
- `tools/`: Development and debug scripts (ignore in production).

### Code Style
- **Python**: We follow PEP 8. Please ensure your code is clean and readable.
- **Frontend**: Keep the "Monochrome Premium" aesthetic. Avoid adding random colors; stick to the black/white/gray theme defined in `styles.css`.
- **Type Hinting**: Use Python type hints (`Optional`, `List`, `Dict`) where possible.

### Submitting Changes

1. **Create a new Branch**:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```
2. **Commit your changes**:
   Write clear, descriptive commit messages.
   ```bash
   git commit -m "feat: Add support for PDF extraction in CLI"
   ```
   *We use Conventional Commits (e.g., `feat:`, `fix:`, `docs:`, `style:`).*

3. **Push to your fork**:
   ```bash
   git push origin feat/your-feature-name
   ```

4. **Open a Pull Request**:
   - Go to the original repository.
   - Click "New Pull Request".
   - Describe your changes in detail. Attach screenshots if you modified the UI.

---

## 🧪 Testing

Before submitting, please verify:
1. The application starts without errors.
2. Both OpenAI and Gemini providers work (if you have keys).
3. The CLI tool functions correctly.

## 🐞 Reporting Bugs

If you find a bug, please create an Issue using the following template:
- **Describe the bug**: What happened?
- **To Reproduce**: Steps to reproduce the behavior.
- **Expected behavior**: What you expected to happen.
- **Screenshots**: If applicable.
- **Environment**: OS, Python version.

## 📜 License
By contributing, you agree that your contributions will be licensed under its MIT License.

---
**Happy Coding!** 🖤
