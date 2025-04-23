import os
import re
import markdown
import openai
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from dotenv import load_dotenv

# Global variable to store the current log file name
current_log_file = None

# Setup logging for AI responses
def log_ai_response(original_text, enhanced_text, model='openai', elapsed=0, input_file=None):
    """Log the original and enhanced text to a file for review"""
    global current_log_file
    
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a log filename with timestamp if it doesn't exist yet
    if current_log_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_base = os.path.basename(input_file).replace('.md', '') if input_file else 'conversion'
        current_log_file = os.path.join(log_dir, f'ai_responses_{model}_{file_base}_{timestamp}.log')
        
        # Create the log file with a header
        with open(current_log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== AI Enhancement Log for {file_base} using {model} ===\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Input file: {input_file}\n\n")
    
    # Append to the log file
    with open(current_log_file, 'a', encoding='utf-8') as f:
        f.write(f"--- Response at {datetime.now().strftime('%H:%M:%S')} (took {elapsed:.2f}s) ---\n")
        f.write(f"Original: {original_text}\n\n")
        f.write(f"Enhanced: {enhanced_text}\n\n")
        f.write("=" * 80 + "\n")
    
    return current_log_file

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
        # Set the API key for OpenAI
        openai.api_key = OPENAI_API_KEY
        
        # Print OpenAI version for debugging
        try:
            print(f"OpenAI version: {openai.__version__}")
        except AttributeError:
            print("OpenAI version: unknown")
            
        # Check if we're using v0.28.0 (which has both old and new APIs)
        if hasattr(openai, 'ChatCompletion'):
            print("Using OpenAI API with ChatCompletion")
            USE_CHAT_COMPLETION = True
        else:
            print("Using OpenAI API with different interface")
            USE_CHAT_COMPLETION = False
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Falling back to no AI mode")
        os.environ["NO_AI"] = "1"

def convert_md_to_docx(input_file, output_file=None, document_order_file=None, template_file=None, current_file=None, total_files=None, enable_logging=False):
    # Reset the global log file at the start of each conversion
    global current_log_file
    current_log_file = None
    # Show progress if processing multiple files
    if current_file is not None and total_files is not None:
        print(f"Processing file {current_file} of {total_files}: {os.path.basename(input_file)}")
    
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
                        print(f"\nEnhancing paragraph: {original_text[:50]}...")
                        # Use OpenAI to enhance the text
                        try:
                            start_time = time.time()
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful assistant that enhances text to make it more professional and engaging."},
                                    {"role": "user", "content": f"Enhance this text to make it more professional and engaging, but keep the same meaning and length similar: {original_text}"}
                                ],
                                max_tokens=150
                            )
                            elapsed = time.time() - start_time
                            
                            # Extract the enhanced text
                            try:
                                # Try the dictionary access method first (most common)
                                enhanced_text = response.choices[0].message['content'].strip()
                                print(f"AI enhancement took {elapsed:.2f} seconds")
                                print(f"Original: {original_text[:50]}...")
                                print(f"Enhanced: {enhanced_text[:50]}...")
                                
                                # Log the AI response to a file if logging is enabled
                                if enable_logging:
                                    log_file = log_ai_response(original_text, enhanced_text, 'openai', elapsed, input_file)
                                    if os.path.exists(log_file) and current_log_file == log_file:
                                        # Only print the log file path once per run
                                        if paragraph_index == 0:
                                            print(f"AI responses being logged to: {log_file}")
                            except (KeyError, TypeError, AttributeError):
                                # Fall back to direct attribute access if needed
                                try:
                                    enhanced_text = response.choices[0].message.content.strip()
                                    print(f"AI enhancement took {elapsed:.2f} seconds")
                                    print(f"Original: {original_text[:50]}...")
                                    print(f"Enhanced: {enhanced_text[:50]}...")
                                    
                                    # Log the AI response to a file
                                    log_file = log_ai_response(original_text, enhanced_text, 'openai', elapsed, input_file)
                                    if os.path.exists(log_file) and current_log_file == log_file:
                                        # Only print the log file path once per run
                                        if paragraph_index == 0:
                                            print(f"AI responses being logged to: {log_file}")
                                except (AttributeError, TypeError):
                                    # Last resort fallback
                                    print(f"Warning: Could not extract enhanced text, using original")
                                    enhanced_text = original_text
                        except Exception as e:
                            print(f"Error calling OpenAI API: {e}")
                            enhanced_text = original_text
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
    
    # Ensure required styles exist
    def ensure_style_exists(style_name, style_type):
        try:
            # Try to access the style to see if it exists
            doc.styles[style_name]
            print(f"Style '{style_name}' already exists")
        except KeyError:
            # Style doesn't exist, create it
            print(f"Creating style '{style_name}'")
            from docx.enum.style import WD_STYLE_TYPE
            if style_type == 'paragraph':
                style_type_enum = WD_STYLE_TYPE.PARAGRAPH
                new_style = doc.styles.add_style(style_name, style_type_enum)
                # Copy properties from Normal style as a base
                base_style = doc.styles['Normal']
                new_style.font.name = base_style.font.name
                new_style.font.size = base_style.font.size
            elif style_type == 'table':
                # For table styles, we can't easily create them
                # We'll handle this separately when creating tables
                print(f"Note: Table style '{style_name}' will be handled during table creation")
                return None
            return new_style
    
    # Ensure list styles exist
    ensure_style_exists('List Bullet', 'paragraph')
    ensure_style_exists('List Number', 'paragraph')
    ensure_style_exists('Table Grid', 'table')
    
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
            try:
                doc.add_paragraph(li.get_text(), style='List Bullet')
            except KeyError:
                # Fallback if style doesn't exist despite our efforts
                para = doc.add_paragraph(li.get_text())
                para.style = 'Normal'
                para.paragraph_format.left_indent = Inches(0.25)
                run = para.add_run('• ', 0)  # Add bullet at beginning
    
    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li')):
            try:
                doc.add_paragraph(li.get_text(), style='List Number')
            except KeyError:
                # Fallback if style doesn't exist despite our efforts
                para = doc.add_paragraph(li.get_text())
                para.style = 'Normal'
                para.paragraph_format.left_indent = Inches(0.25)
                run = para.add_run(f"{i+1}. ", 0)  # Add number at beginning
    
    # Process tables
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        if rows:
            # Get headers
            headers = [th.get_text() for th in rows[0].find_all(['th', 'td'])]
            
            # Create table in Word
            word_table = doc.add_table(rows=len(rows), cols=len(headers))
            
            # Apply basic table formatting since we can't rely on styles
            try:
                word_table.style = 'Table Grid'
            except KeyError:
                # Apply manual formatting if style doesn't exist
                print("Applying manual table formatting")
                from docx.enum.table import WD_TABLE_ALIGNMENT
                word_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                
                # Add borders to all cells
                from docx.shared import Pt
                from docx.enum.text import WD_ALIGN_PARAGRAPH
                for row in word_table.rows:
                    for cell in row.cells:
                        # Add borders (if possible)
                        try:
                            for border in ['top', 'bottom', 'left', 'right']:
                                setattr(cell.borders, border, True)
                        except AttributeError:
                            pass  # If we can't set borders, continue anyway
            
            # Add header row
            for i, header in enumerate(headers):
                cell = word_table.cell(0, i)
                cell.text = header
                # Make header bold if possible
                try:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.bold = True
                except AttributeError:
                    pass  # If we can't make it bold, continue anyway
            
            # Add data rows
            for i, row in enumerate(rows[1:], start=1):
                cells = row.find_all(['td', 'th'])
                for j, cell in enumerate(cells):
                    word_table.cell(i, j).text = cell.get_text()
    
    # Look for paragraphs that might be tables but weren't properly formatted
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        # Check if this looks like a pipe-separated table (at least 3 pipe characters)
        if text.count('|') >= 3 and '|' in text[:10]:
            print(f"Converting text to table: {text[:50]}...")
            
            # Split into rows
            rows = text.split('\n')
            if len(rows) == 1:
                rows = [text]  # Single line table
                
            # Count the maximum number of cells in any row
            max_cols = 0
            for row in rows:
                if row.strip():
                    cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                    max_cols = max(max_cols, len(cells))
            
            if max_cols == 0:
                continue  # Skip if no valid cells found
                
            # Create a new Word table
            word_table = doc.add_table(rows=len(rows), cols=max_cols)
            try:
                word_table.style = 'Table Grid'
            except KeyError:
                # Apply manual formatting if style doesn't exist
                print("Applying manual table formatting")
                from docx.enum.table import WD_TABLE_ALIGNMENT
                word_table.alignment = WD_TABLE_ALIGNMENT.CENTER
                
                # Add borders to all cells
                for row in word_table.rows:
                    for cell in row.cells:
                        # Add borders (if possible)
                        try:
                            for border in ['top', 'bottom', 'left', 'right']:
                                setattr(cell.borders, border, True)
                        except AttributeError:
                            pass  # If we can't set borders, continue anyway
            
            # Process each row
            for i, row_text in enumerate(rows):
                if not row_text.strip():
                    continue  # Skip empty rows
                    
                # Split the row by pipe character
                cells = [cell.strip() for cell in row_text.split('|') if cell.strip()]
                
                # Add cells to the table
                for j, cell_text in enumerate(cells):
                    if j < max_cols:  # Ensure we don't exceed the table dimensions
                        cell = word_table.cell(i, j)
                        
                        # Clean up the cell text (remove ** markers)
                        clean_text = cell_text.replace('**', '')
                        cell.text = clean_text
                        
                        # Make header row bold
                        if i == 0 or '**' in cell_text:
                            try:
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.bold = True
                            except AttributeError:
                                pass  # If we can't make it bold, continue anyway
    
    # Process code blocks
    for pre in soup.find_all('pre'):
        p = doc.add_paragraph()
        code_text = pre.get_text()
        p.add_run(code_text).font.name = 'Courier New'
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Save the document
    print(f"Saving document to: {output_file}")
    doc.save(output_file)
    
    # Verify file was created
    if os.path.exists(output_file):
        print(f"Conversion complete. Output saved to {output_file} ({os.path.getsize(output_file)} bytes)")
    else:
        print(f"WARNING: Output file {output_file} was not created!")
    
    return output_file

# Main function to handle command line arguments and batch processing
if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Convert markdown files to DOCX format')
    parser.add_argument('input_file', nargs='?', help='Input markdown file or document_order.json')
    parser.add_argument('output_file', nargs='?', help='Output DOCX file')
    parser.add_argument('--template', default=None, help='DOCX template file to use for styling')
    parser.add_argument('--no-openai', action='store_true', help='Disable OpenAI processing')
    parser.add_argument('--log', action='store_true', help='Enable detailed logging of AI responses')
    args = parser.parse_args()
    
    # Set NO_AI environment variable if --no-openai flag is provided
    if args.no_openai:
        os.environ['NO_AI'] = '1'
        print("AI processing disabled")
    
    # Get template path
    template_path = args.template
    if not template_path and os.path.exists('template.docx'):
        template_path = 'template.docx'
        print("Using template.docx from current directory")
    elif template_path and os.path.exists(template_path):
        print(f"Using template: {template_path}")
    else:
        template_path = None
        print("No template specified, creating new document")
    
    # Determine if input is a markdown file or document_order.json
    if not args.input_file:
        # No input file specified, try to use document_order.json
        if os.path.exists('document_order.json'):
            args.input_file = 'document_order.json'
            print("Using document_order.json as input")
        else:
            print("Error: No input file specified and document_order.json not found")
            sys.exit(1)
    
    # Check if input is a markdown file
    if args.input_file.endswith('.md'):
        # Process a single markdown file
        md_file = args.input_file
        
        # Generate output filename if not provided
        if not args.output_file:
            base_name = os.path.splitext(os.path.basename(md_file))[0]
            output_file = f"{base_name}_Output.docx"
            # Ensure output directory exists
            if not os.path.exists('output'):
                os.makedirs('output')
            output_path = os.path.join('output', output_file)
        else:
            output_path = args.output_file
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
        
        print(f"Converting {md_file} to {output_path}")
        # Convert the file
        convert_md_to_docx(md_file, output_path, None, template_path, enable_logging=args.log)
        
    else:
        # Assume it's a document_order.json file
        try:
            # Check if file exists
            if not os.path.exists(args.input_file):
                print(f"Error: Input file {args.input_file} not found")
                sys.exit(1)
                
            # Load document order from JSON file
            with open(args.input_file, 'r') as f:
                doc_order = json.load(f)
            
            # Sort documents by order field
            doc_order.sort(key=lambda x: x.get('order', 0))
            
            # Process each document in order
            total_files = len(doc_order)
            for i, doc in enumerate(doc_order, 1):
                md_file = doc.get('filename')
                
                # Check if file exists in markdown directory first
                md_path = os.path.join('markdown', md_file)
                if not os.path.exists(md_path):
                    # Try current directory
                    md_path = md_file
                    if not os.path.exists(md_path):
                        print(f"Warning: File {md_file} not found, skipping")
                        continue
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(md_file))[0]
                output_file = f"{base_name}_Output.docx"
                
                # Ensure output directory exists
                if not os.path.exists('output'):
                    os.makedirs('output')
                output_path = os.path.join('output', output_file)
                
                # Convert the file
                convert_md_to_docx(md_path, output_path, args.input_file, template_path, i, total_files, args.log)
                
            print(f"Batch processing complete. {total_files} files processed.")
            
        except json.JSONDecodeError:
            print(f"Error: {args.input_file} is not a valid JSON file")
            print("If you're trying to convert a markdown file, make sure it has a .md extension")
        except Exception as e:
            print(f"Error processing document order: {e}")
