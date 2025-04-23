import markdown
import os
import sys
import json
import re
import time
import anthropic
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Anthropic client
# Get API key from environment variables (loaded from .env file)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not ANTHROPIC_API_KEY:
    print("Warning: No Claude API key found. Please set the ANTHROPIC_API_KEY in your .env file.")
    print("Example .env file content:\nANTHROPIC_API_KEY=sk-ant-api03-your-key-here")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def process_content_with_claude(text):
    # First, identify tables and bullet lists to process
    bullet_pattern = re.compile(r'(?:^|\n)((?:[ \t]*[-*+] .+\n?)+)', re.MULTILINE)
    table_pattern = re.compile(r'(?:^|\n)(\|[^\n]+\|\n(?:\|[-:\|\s]+\|\n)?(?:\|[^\n]+\|\n)+)', re.MULTILINE)
    
    # Find all matches
    bullet_matches = list(bullet_pattern.finditer(text))
    table_matches = list(table_pattern.finditer(text))
    
    # Combine all matches for processing
    all_matches = bullet_matches + table_matches
    if not all_matches:
        return text  # Nothing to process
    
    # Sort matches by position in text
    all_matches.sort(key=lambda x: x.start())
    
    print(f"Found {len(bullet_matches)} bullet lists and {len(table_matches)} tables to process")
    
    # Process each match with throttling
    results = {}
    for i, match in enumerate(all_matches):
        content = match.group(0)
        
        # Determine if this is a bullet list or table
        is_table = match in table_matches
        
        if is_table:
            system_prompt = "You are a helpful assistant that formats markdown tables properly."
            user_prompt = f"Format the following markdown table to ensure it's properly structured with aligned columns. Fix any formatting issues but preserve all data and column headers. If there are cells with just dashes like '|----|', replace them with empty cells.\n\n{content}\n"
        else:  # bullet list
            system_prompt = "You are a helpful assistant that converts bullet points to flowing paragraphs."
            user_prompt = f"Rewrite the following bullet points as a clear, flowing paragraph. Do not use any bullet points or lists.\n\n{content}\n"
        
        # Add throttling - wait between API calls
        if i > 0:
            print(f"Processing item {i+1}/{len(all_matches)}...")
            time.sleep(0.33)  # 0.33 seconds between calls (≈3 requests per second)
            
        try:
            message = client.messages.create(
                model="claude-3-opus-20240229",  # Using Claude's most capable model
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract the response content
            response_content = message.content[0].text
            
            if is_table:
                # For tables, we want to preserve the markdown structure
                results[match.span()] = '\n' + response_content.strip() + '\n'
            else:
                # For bullet points, we want to convert to paragraphs
                results[match.span()] = '\n' + response_content.strip() + '\n'
                
        except Exception as e:
            print(f"Claude API error: {e}")
            results[match.span()] = content  # Fallback to original
    
    # Replace all matches with their processed versions
    # We need to replace from end to beginning to avoid offset issues
    spans = sorted(results.keys(), reverse=True)
    result_text = text
    for span in spans:
        result_text = result_text[:span[0]] + results[span] + result_text[span[1]:]
        
    return result_text

# Usage: python md_to_docx_claude.py [document_order.json] [template.docx]
# If document_order.json is not specified, default to all .md files in the current directory
# If template.docx is not specified, create a new document

def get_files_from_order(order_file):
    with open(order_file, 'r') as f:
        order_data = json.load(f)
    # Extract filenames from the order data
    return [item['filename'] for item in sorted(order_data, key=lambda x: x['order'])]

def get_markdown_files():
    if len(sys.argv) > 1 and sys.argv[1].endswith('.md'):
        print(f"Using files from command line: {sys.argv[1:]}")
        return sys.argv[1:]
    else:
        if not os.path.exists('markdown'):
            print("ERROR: 'markdown' directory not found! Please create a 'markdown' directory and add markdown files.")
            return []
        md_files = [f for f in os.listdir('markdown') if f.endswith('.md')]
        print(f"Markdown files found in 'markdown': {md_files}")
        return md_files

def get_template_path():
    # Check if template is provided as command line argument
    if len(sys.argv) > 2 and sys.argv[2].endswith('.docx'):
        template_path = sys.argv[2]
        if os.path.exists(template_path):
            print(f"Using template from command line: {template_path}")
            return template_path
        else:
            print(f"Warning: Template {template_path} not found, using default template.")
    
    # Check for template.docx in current directory
    if os.path.exists('template.docx'):
        print("Using template.docx from current directory")
        return 'template.docx'
    
    # No template found
    print("No template found, creating new document")
    return None

def html_to_docx_content(html_content, doc, section_title=None):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Add section title if provided
    if section_title:
        heading = doc.add_heading(section_title, level=1)
        heading.style.font.color.rgb = RGBColor(0, 0, 139)  # Dark blue
    
    # Process each element in the HTML
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'table']):
        if element.name.startswith('h') and len(element.name) == 2:
            # Handle headings
            level = int(element.name[1])
            doc.add_heading(element.get_text(), level=level)
        elif element.name == 'p':
            # Handle paragraphs
            p = doc.add_paragraph()
            p.add_run(element.get_text())
        elif element.name == 'table':
            # Handle tables using our custom table processor
            process_table(str(element), doc)
        elif element.name in ['ul', 'ol']:
            # Handle lists
            for li in element.find_all('li', recursive=False):
                p = doc.add_paragraph(style='List Bullet' if element.name == 'ul' else 'List Number')
                p.add_run(li.get_text().strip())
    
    # Add a page break after each section (except the last one)
    doc.add_page_break()

def process_table(table_html, doc):
    soup = BeautifulSoup(table_html, 'html.parser')
    table = soup.find('table')
    
    if not table:
        return
    
    rows = table.find_all('tr')
    if not rows:
        return
    
    # Get the number of columns from the first row
    first_row = rows[0]
    cells = first_row.find_all(['th', 'td'])
    num_cols = len(cells)
    
    # Create a table in the Word document
    doc_table = doc.add_table(rows=len(rows), cols=num_cols)
    doc_table.style = 'Table Grid'
    
    # Process each row
    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        
        # Check if this is a header row (first row or contains th elements)
        is_header_row = (i == 0) or any(cell.name == 'th' for cell in cells)
        
        # Check if this is the last row (often contains totals)
        is_last_row = (i == len(rows) - 1)
        
        # Process each cell in the row
        for j, cell in enumerate(cells):
            if j < num_cols:  # Ensure we don't exceed the number of columns in the Word table
                # Get cell content
                cell_content = cell.get_text().strip()
                
                # Add content to the Word table cell
                doc_cell = doc_table.cell(i, j)
                cell_para = doc_cell.paragraphs[0]
                run = cell_para.add_run(cell_content)
                
                # Header row styling
                if is_header_row:
                    run.bold = True
                    # Set text color to white for header rows (we can't set background color easily)
                    run.font.color.rgb = RGBColor(0, 0, 139)  # Dark blue text instead
                    # Apply bold formatting
                    run.bold = True
                
                # Price columns left alignment
                if j >= len(cells) - 2 or 'price' in cell_content.lower() or '$' in cell_content:
                    cell_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Last row (total/subtotal) styling
                if is_last_row or 'total' in cell_content.lower() or 'subtotal' in cell_content.lower():
                    run.bold = True
                    # Add a top border
                    doc_cell.top = Pt(1)
                
                # Bold any cell with 'total' or 'subtotal' in it
                if 'total' in cell_content.lower() or 'subtotal' in cell_content.lower():
                    run.bold = True
    
    # Add some space after the table
    doc.add_paragraph()

def convert_and_merge_to_docx(md_files, template_path=None, md_dir='markdown', output_dir='output', output_file=None, use_claude=True):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # If no output file is specified, use the first markdown filename as the base
    if output_file is None and md_files:
        base_filename = os.path.splitext(md_files[0])[0]
        output_file = f"{base_filename}_Output.docx"
    else:
        output_file = 'merged_output.docx'
        
    output_path = os.path.join(output_dir, output_file)
    
    if not md_files:
        print("No markdown files provided to merge! Exiting.")
        return
    
    # Create a new document or use template
    if template_path:
        doc = Document(template_path)
    else:
        doc = Document()
        # Set up default styles
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Calibri'
        font.size = Pt(11)
    
    # Process each markdown file
    for md_file in md_files:
        md_path = os.path.join(md_dir, md_file)
        if not os.path.exists(md_path):
            print(f"Warning: {md_path} not found, skipping.")
            continue
        
        print(f"Merging: {md_path}")
        with open(md_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Improve table formatting
        # 1. Clean up dashed lines in table cells - replace with actual content
        # This pattern looks for cells with only dashes and replaces them with empty cells
        # First, handle cells that are just dashes
        text = re.sub(r'\|\s*-+\s*\|', '| |', text)
        # Then handle cells with a pattern like |---------|  
        text = re.sub(r'\|(\s*-+\s*)(?=\|)', '| ', text)
        # Finally handle cells with a pattern like |---------|  
        text = re.sub(r'(?<=\|)(\s*-+\s*)\|', ' |', text)
        
        # 2. Make sure tables have proper headers and separators
        # Find tables without proper separator lines and add them
        table_pattern = re.compile(r'(\|[^\n]+\|)\n(?!\|[-:\|\s]+\|)', re.MULTILINE)
        text = table_pattern.sub(r'\1\n|' + '-' * 10 + '|\n', text)
        
        # 3. Remove extra separator lines in tables (keeping only one)
        text = re.sub(r'(\n\|[-:\|\s]+\|\n)\|[-:\|\s]+\|\n', r'\1', text)
        
        # 4. Ensure proper spacing around tables
        text = re.sub(r'(\n\|[^\n]+\|\n)(?!\|)', r'\1\n', text)
        
        # Process content (bullets and tables) using Claude (if enabled)
        if use_claude:
            try:
                text = process_content_with_claude(text)
            except Exception as e:
                print(f"Error using Claude API: {e}")
                print("Continuing without Claude processing...")
        
        # Convert markdown to HTML
        html_content = markdown.markdown(text, extensions=['tables', 'attr_list'])
        
        # Get section title from filename
        section_title = os.path.splitext(os.path.basename(md_file))[0]
        
        # Convert HTML to Word document content
        html_to_docx_content(html_content, doc, section_title)
    
    # Save the document
    doc.save(output_path)
    print(f"Merged {len(md_files)} files into {output_path} with styling.")

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Convert markdown files to Word document using Claude AI')
    parser.add_argument('order_file', nargs='?', default='document_order.json', help='JSON file with document order')
    parser.add_argument('template', nargs='?', default=None, help='Word template file')
    parser.add_argument('--no-claude', action='store_true', help='Disable Claude API calls')
    args = parser.parse_args()
    
    # Determine whether to use Claude
    use_claude = not args.no_claude
    
    # Check for NO_AI environment variable
    if os.environ.get('NO_AI'):
        use_claude = False
    
    if not use_claude:
        print("Claude API calls disabled. Running without processing.")
    
    # Get template path
    template_path = args.template
    if not template_path:
        template_path = get_template_path()
    
    try:
        with open(args.order_file, 'r') as f:
            order_data = json.load(f)
        
        # Extract filenames from the order data
        md_files = [item['filename'] for item in sorted(order_data, key=lambda x: x['order'])]
        
        convert_and_merge_to_docx(md_files, template_path, use_claude=use_claude)
        print("Conversion completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to processing all markdown files in the directory
        md_files = get_markdown_files()
        if not md_files:
            print("No markdown files found.")
            sys.exit(1)
        convert_and_merge_to_docx(md_files, template_path, use_claude=use_claude)
        print("Fallback conversion completed!")
