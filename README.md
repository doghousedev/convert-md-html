# Markdown to HTML Converter

A Python utility that converts multiple markdown files into a single HTML document with AI-enhanced paragraph formatting.

## Features

- Convert multiple markdown files to a single HTML document
- Use OpenAI to paraphrase bullet points into flowing paragraphs
- Control the order of markdown files using a JSON configuration
- Apply custom styling with CSS
- Easy deployment to Netlify

## Requirements

- Python 3.6+
- OpenAI API key
- Markdown library

## Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd convert-md-html

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage (processes all .md files in the markdown directory)
python md_to_html.py

# Use a specific order file
python md_to_html.py order.json
```

## Configuration

Create an `order.json` file to specify the order of markdown files:

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
