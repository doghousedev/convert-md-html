import os
import re
import markdown
import openai
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup
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

# Use the API key from environment variable
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

def convert_md_to_html(input_file, output_file=None, document_order_file=None, enable_logging=False):
    # Reset the global log file at the start of each conversion
    global current_log_file
    current_log_file = None
    # Read the markdown file
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Generate output filename based on input filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_file = f"{base_name}_Output.html"
        # If output directory exists, put the file there
        if os.path.exists('output'):
            output_file = os.path.join('output', output_file)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process tables that were already detected by markdown parser
    for table in soup.find_all('table'):
        table['class'] = 'table table-bordered table-striped'
        
        # Add Bootstrap styling to table headers
        if table.thead:
            table.thead['class'] = 'thead-dark'
        
        # If no thead exists, style the first row as header
        if table.tr:
            headers = table.tr.find_all(['th', 'td'])
            for header in headers:
                if header.name == 'td':
                    header.name = 'th'
                header['scope'] = 'col'
                header['style'] = 'background-color: #343a40; color: white;'
        
        # Style the table cells
        for row in table.find_all('tr'):
            for cell in row.find_all(['td', 'th']):
                cell['style'] = 'padding: 8px; vertical-align: middle;'
    
    # Look for text that might be tables but wasn't properly formatted
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        # Check if this looks like a pipe-separated table (at least 3 pipe characters)
        if text.count('|') >= 3:
            print(f"Converting pipe-separated text to table: {text[:50]}...")
            
            # Split into rows
            rows = text.split('\n')
            if len(rows) == 1:
                # Try to find adjacent paragraphs that might be part of the same table
                table_rows = [text]
                next_sibling = p.next_sibling
                while next_sibling:
                    if isinstance(next_sibling, str) and next_sibling.strip() == '':
                        next_sibling = next_sibling.next_sibling
                        continue
                    if hasattr(next_sibling, 'name') and next_sibling.name == 'p':
                        sibling_text = next_sibling.get_text()
                        if '|' in sibling_text:
                            table_rows.append(sibling_text)
                            temp = next_sibling
                            next_sibling = next_sibling.next_sibling
                            # Mark this paragraph for removal since we're including it in the table
                            temp['data-table-row'] = 'true'
                        else:
                            break
                    else:
                        break
                rows = table_rows
            
            # Create a new table
            new_table = soup.new_tag('table')
            new_table['class'] = 'table table-bordered table-striped'
            
            # Check if we have a separator row (row with dashes and pipes)
            has_separator = False
            header_row_index = -1
            for i, row in enumerate(rows):
                if row.strip().replace('|', '').replace('-', '').replace(' ', '') == '':
                    has_separator = True
                    header_row_index = i - 1  # The row before the separator is the header
                    break
            
            # If we have a separator row, create thead and tbody
            thead = None
            tbody = soup.new_tag('tbody')
            if has_separator and header_row_index >= 0:
                thead = soup.new_tag('thead')
                thead['class'] = 'thead-dark'
            
            # Process each row
            for i, row in enumerate(rows):
                # Skip separator rows (rows with only |, -, and spaces)
                if row.strip().replace('|', '').replace('-', '').replace(' ', '') == '':
                    continue
                
                tr = soup.new_tag('tr')
                
                # Split the row by pipe character and remove empty cells at the beginning/end
                cells = row.split('|')
                if cells and not cells[0].strip():
                    cells.pop(0)
                if cells and not cells[-1].strip():
                    cells.pop()
                
                for cell_text in cells:
                    # Determine if this is a header row
                    is_header = (has_separator and i == header_row_index) or (i == 0 and not has_separator) or '**' in cell_text
                    
                    # Create appropriate cell type
                    if is_header:
                        cell = soup.new_tag('th')
                        cell['scope'] = 'col'
                        cell['style'] = 'background-color: #343a40; color: white; padding: 8px; vertical-align: middle;'
                    else:
                        cell = soup.new_tag('td')
                        cell['style'] = 'padding: 8px; vertical-align: middle;'
                    
                    # Clean up the cell text (remove ** markers and extra whitespace)
                    clean_text = cell_text.strip().replace('**', '')
                    cell.string = clean_text
                    tr.append(cell)
                
                # Add the row to the appropriate section
                if has_separator and i == header_row_index:
                    thead.append(tr)
                else:
                    if i != header_row_index and not (row.strip().replace('|', '').replace('-', '').replace(' ', '') == ''):
                        tbody.append(tr)
            
            # Add thead and tbody to the table
            if thead:
                new_table.append(thead)
            new_table.append(tbody)
            
            # Replace the original paragraph with the new table
            p.replace_with(new_table)
            
            # Remove any paragraphs that were marked as table rows
            for row_p in soup.find_all('p', attrs={'data-table-row': 'true'}):
                row_p.decompose()
    
    # Process bullet lists
    for ul in soup.find_all('ul'):
        ul['class'] = 'list-group'
        for li in ul.find_all('li'):
            li['class'] = 'list-group-item'
    
    # Process paragraphs for AI enhancement if enabled
    if os.environ.get('NO_AI') != '1':
        try:
            # Find all paragraphs
            paragraphs = soup.find_all(['p', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            # Initialize paragraph index for logging
            paragraph_index = 0
            
            for p in paragraphs:
                original_text = p.get_text()
                if len(original_text.split()) > 5:  # Only process paragraphs with more than 5 words
                    try:
                        # Use OpenAI to enhance the text
                        print(f"Enhancing: {original_text[:50]}...")
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
                            print(f"\n=== OpenAI Response ===\nOriginal: {original_text[:100]}...\nEnhanced: {enhanced_text[:100]}...\n====================\n")
                            print(f"AI enhancement took {elapsed:.2f} seconds")
                            
                            # Log the AI response to a file if logging is enabled
                            if enable_logging:
                                log_file = log_ai_response(original_text, enhanced_text, 'openai', elapsed, input_file)
                                if os.path.exists(log_file) and current_log_file == log_file:
                                    # Only print the log file path once per run
                                    if paragraph_index == 0:
                                        print(f"AI responses being logged to: {log_file}")
                            
                            # Update the paragraph content with the enhanced text
                            p.string = enhanced_text
                            
                            # Increment paragraph index for logging
                            paragraph_index += 1
                            
                        except (KeyError, TypeError, AttributeError):
                            # Fall back to direct attribute access if needed
                            try:
                                enhanced_text = response.choices[0].message.content.strip()
                                print(f"\n=== OpenAI Response ===\nOriginal: {original_text[:100]}...\nEnhanced: {enhanced_text[:100]}...\n====================\n")
                                print(f"AI enhancement took {elapsed:.2f} seconds")
                                
                                # Log the AI response to a file if logging is enabled
                                if enable_logging:
                                    log_file = log_ai_response(original_text, enhanced_text, 'openai', elapsed, input_file)
                                    if os.path.exists(log_file) and current_log_file == log_file:
                                        # Only print the log file path once per run
                                        if paragraph_index == 0:
                                            print(f"AI responses being logged to: {log_file}")
                                
                                # Update the paragraph content with the enhanced text
                                p.string = enhanced_text
                                
                                # Increment paragraph index for logging
                                paragraph_index += 1
                                
                            except (AttributeError, TypeError):
                                # Last resort fallback
                                print(f"Warning: Could not extract enhanced text, using original")
                                enhanced_text = original_text
                                p.string = enhanced_text
                    except Exception as e:
                        print(f"Error calling OpenAI API: {e}")
                        # Keep the original text if there's an error
        except Exception as e:
            print(f"Error processing with AI: {e}")
    
    # Create a complete HTML document
    html_template = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Converted Markdown</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ padding: 20px; max-width: 800px; margin: 0 auto; }}
            .table {{ margin-top: 20px; margin-bottom: 20px; }}
            pre {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
            code {{ color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            {soup.prettify()}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    '''
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    # Write the HTML to the output file
    print(f"Saving HTML to: {output_file}")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_template)
        print(f"Conversion complete. Output saved to {output_file} ({os.path.getsize(output_file)} bytes)")
    except Exception as e:
        print(f"Error saving output file: {e}")
    return output_file

# Main function to handle command line arguments
if __name__ == '__main__':
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Convert markdown files to HTML format')
    parser.add_argument('input_file', nargs='?', help='Input markdown file or document_order.json')
    parser.add_argument('output_file', nargs='?', help='Output HTML file')
    parser.add_argument('--no-openai', action='store_true', help='Disable OpenAI processing')
    parser.add_argument('--log', action='store_true', help='Enable detailed logging of AI responses')
    args = parser.parse_args()
    
    # Set NO_AI environment variable if --no-openai flag is provided
    if args.no_openai:
        os.environ['NO_AI'] = '1'
        print("AI processing disabled")
    
    # Check if input file exists
    if not args.input_file or not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found")
        exit(1)
    
    # Check if it's a markdown file or document_order.json
    if args.input_file.endswith('.md'):
        # It's a markdown file, convert it directly
        md_file = args.input_file
        
        # Generate output filename if not provided
        if not args.output_file:
            base_name = os.path.splitext(os.path.basename(md_file))[0]
            output_path = f"{base_name}_Output.html"
            # If output directory exists, put the file there
            if os.path.exists('output'):
                output_path = os.path.join('output', output_path)
        else:
            output_path = args.output_file
        
        print(f"Converting {md_file} to {output_path}")
        # Convert the file with logging if enabled
        convert_md_to_html(md_file, output_path, None, args.log)
        
    else:
        # Assume it's a document_order.json file
        try:
            with open(args.input_file, 'r') as f:
                document_order = json.load(f)
            
            # Check if it's a valid document order file
            if not isinstance(document_order, list):
                print(f"Error: Invalid document order file format in {args.input_file}")
                exit(1)
            
            # Process each file in the document order
            total_files = len(document_order)
            print(f"Processing {total_files} files from document order")
            
            for i, doc in enumerate(document_order, 1):
                # Get the markdown file path
                if isinstance(doc, dict) and 'filename' in doc:
                    # Handle the case where doc is a dictionary with a filename field
                    md_file = doc['filename']
                else:
                    # Handle the case where doc is a string (for backward compatibility)
                    md_file = doc
                
                md_path = os.path.join('markdown', md_file)
                if not os.path.exists(md_path):
                    print(f"Warning: File {md_path} not found, skipping")
                    continue
                
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(md_path))[0]
                output_file = f"{base_name}_Output.html"
                output_path = os.path.join('output', output_file)
                
                # Convert the file with logging if enabled
                convert_md_to_html(md_path, output_path, args.input_file, args.log)
                
            print(f"Batch processing complete. {total_files} files processed.")
            
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {args.input_file}")
            exit(1)
        except Exception as e:
            print(f"Error processing document order: {e}")
            exit(1)
