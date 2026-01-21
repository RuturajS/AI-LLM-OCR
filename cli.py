import typer
import os
import json
from typing import Optional
from pathlib import Path
from rich.console import Console
from rich.table import Table
from app.ocr_engine import OCREngine

app = typer.Typer(help="AI Smart OCR - Extract text using OpenAI or Gemini.")
console = Console()
engine = OCREngine()

@app.command()
def extract(
    image_path: str = typer.Argument(..., help="Path to image or PDF file to process."),
    prompt: str = typer.Option("Extract all text", help="Specific instruction for the AI (e.g., 'Find the total')."),
    provider: str = typer.Option("openai", help="AI Provider to use: 'openai' or 'gemini'."),
    openai_key: Optional[str] = typer.Option(None, help="OpenAI API Key (overrides env var OPENAI_API_KEY)."),
    gemini_key: Optional[str] = typer.Option(None, help="Gemini API Key (overrides env var GEMINI_API_KEY)."),
    model: Optional[str] = typer.Option(None, help="Specific model to use (e.g., gpt-4o, gemini-1.5-flash)."),
    output: Optional[str] = typer.Option(None, help="Path to save output file (e.g., result.json)."),
    verbose: bool = typer.Option(False, help="Enable verbose logging.")
):
    """
    Extract text/data from an image using AI.
    
    Examples:
    
    python cli.py extract invoice.png --provider openai --openai-key sk-...
    
    python cli.py extract table.jpg --provider gemini --gemini-key AIza... --prompt "Extract table as CSV"
    
    # Note: Default Gemini model is 'gemini-1.5-flash-001'.
    """
    if not os.path.exists(image_path):
        console.print(f"[bold red]Error:[/bold red] File {image_path} not found.")
        raise typer.Exit(code=1)

    # Resolve API Key
    final_key = None
    if provider.lower() == "openai":
        final_key = openai_key or os.environ.get("OPENAI_API_KEY")
    elif provider.lower() == "gemini":
        final_key = gemini_key or os.environ.get("GEMINI_API_KEY")
    
    if not final_key:
        console.print(f"[bold red]Error:[/bold red] No API Key found for {provider}.")
        console.print(f"Please provide --{provider}-key or set {provider.upper()}_API_KEY environment variable.")
        raise typer.Exit(code=1)

    if verbose:
        console.print(f"[blue]Processing {image_path} with {provider}...[/blue]")

    try:
        with open(image_path, "rb") as f:
            content = f.read()

        result = engine.extract(provider, content, prompt, final_key, model)
        
        if verbose:
            console.print("[green]Extraction successful![/green]")

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(str(result))
            console.print(f"Result saved to {output}")
        else:
            console.print(result)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

@app.command()
def history(
    limit: int = typer.Option(10, help="Number of history items to show.")
):
    """
    Show local extraction history.
    """
    history_file = "history.json"
    if not os.path.exists(history_file):
        console.print("No history found.")
        return

    with open(history_file, "r") as f:
        data = json.load(f)

    table = Table(title="Extraction History")
    table.add_column("Date", style="cyan")
    table.add_column("File", style="magenta")
    table.add_column("Prompt", style="green")

    for item in data[:10]: # Show last 10
        table.add_row(item.get("timestamp", "")[:19], item.get("filename", ""), item.get("prompt", "")[:50])

    console.print(table)

if __name__ == "__main__":
    app()
