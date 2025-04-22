# Markdown to HTML/Word Converter

A Python utility that converts multiple markdown files into a single HTML document or Word document (.docx) with AI-enhanced paragraph formatting.

## Features

- Convert multiple markdown files to a single HTML document or Word document (.docx)
- Use OpenAI to paraphrase bullet points into flowing paragraphs
- Control the order of markdown files using a JSON configuration
- Apply custom styling with CSS for HTML output
- Use Word templates for consistent document formatting
- Easy deployment to Netlify for HTML output

## Requirements

- Python 3.6+
- OpenAI API key
- Markdown library
- python-docx library (for Word document output)

## Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd convert-md-html

# Install dependencies
pip install -r requirements.txt
```

## Usage

### HTML Output

```bash
# Basic usage (processes all .md files in the markdown directory)
python md_to_html.py

# Use a specific order file
python md_to_html.py document_order.json
```

### Word Document Output

```bash
# Basic usage (processes all .md files in the markdown directory)
python md_to_docx.py

# Use a specific order file
python md_to_docx.py document_order.json

# Use a specific Word template
python md_to_docx.py document_order.json template.docx
```

## Configuration

Create a `document_order.json` file to specify the order of markdown files:

```json
[
  {"filename": "first_file.md", "order": 1},
  {"filename": "second_file.md", "order": 2},
  {"filename": "third_file.md", "order": 3}
]
```

## OpenAI Integration

Set your OpenAI API key in the script or as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

## License

MIT
