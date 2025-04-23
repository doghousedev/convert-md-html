# Markdown Converter with Claude AI

This extension of the Markdown converter uses Claude AI instead of OpenAI to process markdown files and generate HTML and Word documents with enhanced formatting.

## Features

- Convert markdown files to styled HTML documents
- Convert markdown files to Word documents with consistent formatting
- Use Claude AI to improve bullet point formatting and table structure
- Throttled API calls to prevent rate limiting
- Support for document ordering via JSON configuration

## Requirements

- Python 3.8+
- Required packages (install via `pip install -r requirements.txt`):
  - markdown
  - python-docx
  - beautifulsoup4
  - anthropic
  - python-dotenv

## Setup

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Claude API key:
   - Create a `.env` file in the project root with your API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```
   - Or use the provided helper scripts that set the environment variable directly

## Usage

### Using Helper Scripts (Recommended)

The easiest way to run the converters is using the helper scripts:

```bash
# For HTML conversion
python convert_to_html.py

# For Word document conversion
python convert_to_docx.py
```

### Direct Usage

If you have your API key set in a `.env` file or as an environment variable:

```bash
# Convert markdown to HTML
python md_to_html_claude.py [document_order.json]

# Convert markdown to Word document
python md_to_docx_claude.py [document_order.json] [template.docx]
```

### Command Line Options

Both scripts support the following command line options:

- `--no-claude`: Disable Claude API calls (useful for testing without using API quota)

## File Structure

- `markdown/`: Directory containing your markdown files
- `output/`: Directory where generated HTML and Word documents will be saved
- `template.docx`: Optional Word template for consistent styling
- `document_order.json`: JSON file specifying the order of markdown files

## Benefits Over OpenAI Version

- More generous API quotas
- Better handling of complex tables
- Improved formatting capabilities
- No token limitations for large documents
- Faster processing (3 requests per second vs. 1 per second)
- More reliable API availability
