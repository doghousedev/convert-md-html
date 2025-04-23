# Markdown to HTML/Word Converter

A Python utility that converts multiple markdown files into a single HTML document or Word document (.docx) with AI-enhanced paragraph formatting.

## Features

- Convert multiple markdown files to a single HTML document or Word document (.docx)
- Use OpenAI or Claude AI to enhance formatting and paraphrase bullet points into flowing paragraphs
- Control the order of markdown files using a JSON configuration
- Apply custom styling with CSS for HTML output
- Use Word templates for consistent document formatting
- Dynamic output filenames based on input filename (e.g., `input.md` → `input_Output.html/docx`)
- Unified converter interface to select model and output format
- Easy deployment to Netlify for HTML output

## Requirements

- Python 3.6+
- OpenAI API key (for OpenAI model)
- Claude API key (for Claude model)
- Markdown library
- python-docx library (for Word document output)
- beautifulsoup4 (for HTML parsing)
- python-dotenv (for environment variable management)

## Installation

```bash
# Clone the repository
git clone [your-repo-url]
cd convert-md-html

# Install dependencies
pip install -r requirements.txt
```

## API Key Setup

The converter requires API keys to use AI models for text enhancement. You can set these up in two ways:

### Option 1: Using a .env file (Recommended)

Create a file named `.env` in the project root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_claude_api_key_here
```

**Note:** The `.env` file should not be committed to version control as it contains sensitive information.

### Option 2: Using Environment Variables

Set the API keys as environment variables in your terminal session:

```bash
# PowerShell
$env:OPENAI_API_KEY = "your_openai_api_key_here"
$env:ANTHROPIC_API_KEY = "your_claude_api_key_here"

# Bash/Linux/macOS
export OPENAI_API_KEY="your_openai_api_key_here"
export ANTHROPIC_API_KEY="your_claude_api_key_here"
```

## Usage

### Unified Converter (Recommended)

The easiest way to use the converter is with the unified interface:

```bash
# Convert to HTML using Claude (default)
python convert.py

# Convert to Word document using Claude
python convert.py --format docx

# Convert to HTML using OpenAI
python convert.py --model openai

# Convert to Word document using OpenAI
python convert.py --format docx --model openai

# Convert without using AI
python convert.py --no-ai

# Show help and all available options
python convert.py --help
```

### Individual Converters

**Note:** The individual converter scripts have been moved to the `converters` directory. It's recommended to use the unified converter interface (`convert.py`) instead.

#### HTML Output

```bash
# Using OpenAI
python converters/md_to_html.py

# Using Claude
python converters/md_to_html_claude.py

# Without AI processing
python converters/md_to_html.py --no-ai
```

#### Word Document Output

```bash
# Using OpenAI
python converters/md_to_docx.py

# Using Claude
python converters/md_to_docx_claude.py

# Without AI processing
python converters/md_to_docx.py --no-ai

# Use a specific order file
python converters/md_to_docx.py document_order.json

# Use a specific Word template
python converters/md_to_docx.py document_order.json template.docx
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
