import os
import re
import markdown
import openai
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use the python-md-html key from your OpenAI dashboard
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# If environment variable is not set, warn the user
if not OPENAI_API_KEY:
    print("Warning: No OpenAI API key found. Please set the OPENAI_API_KEY environment variable or add it to your .env file.")
    print("Running without AI processing.")
    os.environ["NO_AI"] = "1"

# Initialize OpenAI client only if we're using AI
if os.environ.get('NO_AI') != '1':
    try:
        # For OpenAI 0.28.0
        client = openai.Client(api_key=OPENAI_API_KEY)
        print("Using OpenAI API v0.28.0")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Falling back to no AI mode")
        os.environ["NO_AI"] = "1"

def convert_md_to_docx(input_file, output_file=None, document_order_file=None, template_file=None):
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Generate output filename based on input filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}_Output.docx"
        # If output directory exists, put the file there
        if os.path.exists('output'):
            output_file = os.path.join('output', output_file)
    
    # Convert markdown to HTML first (for easier parsing)
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # If we're using AI, enhance the content
    if os.environ.get('NO_AI') != '1':
        try:
            # Extract all paragraphs
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                original_text = p.get_text()
                if len(original_text.split()) > 5:  # Only process paragraphs with more than 5 words
                    # Use OpenAI to enhance the text
                    try:
                        # For OpenAI 0.28.0
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant that enhances text to make it more professional and engaging."},
                                {"role": "user", "content": f"Enhance this text to make it more professional and engaging, but keep the same meaning and length similar: {original_text}"}
                            ],
                            max_tokens=150
                        )
                        enhanced_text = response.choices[0].message.content.strip()
                        p.string = enhanced_text
                    except Exception as e:
                        print(f"Error enhancing paragraph: {e}")
                        # Keep the original text if there's an error
        except Exception as e:
            print(f"Error processing with AI: {e}")
    
    # Create a new Word document or use template if provided
    if template_file and os.path.exists(template_file):
        doc = Document(template_file)
        print(f"Using template: {template_file}")
    else:
        doc = Document()
        # Set up the document with some basic styling
        style = doc.styles['Normal']
        style.font.name = 'Calibri'
        style.font.size = Pt(11)
    
    # Process headings
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(heading.name[1])
        doc.add_heading(heading.get_text(), level=level)
    
    # Process paragraphs
    for p in soup.find_all('p'):
        doc.add_paragraph(p.get_text())
    
    # Process lists
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li'):
            doc.add_paragraph(li.get_text(), style='List Bullet')
    
    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li')):
            doc.add_paragraph(li.get_text(), style='List Number')
    
    # Process tables
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if rows:
            # Get headers
            headers = [th.get_text() for th in rows[0].find_all(['th', 'td'])]
            
            # Create table in Word
            word_table = doc.add_table(rows=len(rows), cols=len(headers))
            word_table.style = 'Table Grid'
            
            # Add header row
            for i, header in enumerate(headers):
                word_table.cell(0, i).text = header
            
            # Add data rows
            for i, row in enumerate(rows[1:], start=1):
                cells = row.find_all(['td', 'th'])
                for j, cell in enumerate(cells):
                    word_table.cell(i, j).text = cell.get_text()
    
    # Process code blocks
    for pre in soup.find_all('pre'):
        p = doc.add_paragraph()
        code_text = pre.get_text()
        p.add_run(code_text).font.name = 'Courier New'
    
    # Save the document
    doc.save(output_file)
    
    print(f"Conversion complete. Output saved to {output_file}")
    return output_file
