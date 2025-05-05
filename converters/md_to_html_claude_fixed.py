import markdown
import os
import sys
import json
import re
import time
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up Anthropic client
# Get API key from environment variables (loaded from .env file)
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

if not ANTHROPIC_API_KEY:
    print("Warning: No Claude API key found. Please set the ANTHROPIC_API_KEY in your .env file.")
    print("Example .env file content:\nANTHROPIC_API_KEY=sk-ant-api03-your-key-here")
    sys.exit(1)
else:
    print(f"Using Claude API key: {ANTHROPIC_API_KEY[:5]}...{ANTHROPIC_API_KEY[-5:]}")

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
            
            # Print a preview of the AI response
            preview = response_content.strip()[:100] + "..." if len(response_content.strip()) > 100 else response_content.strip()
            if is_table:
                print(f"\nClaude AI response (table formatting): \n{preview}\n")
                # For tables, we want to preserve the markdown structure
                results[match.span()] = '\n' + response_content.strip() + '\n'
            else:
                print(f"\nClaude AI response (bullet point conversion): \n{preview}\n")
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


def convert_and_merge(md_files, output_file=None, md_dir='markdown', output_dir='output', use_claude=True):
    merged_sections = []
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # If no output file is specified, use the first markdown filename as the base
    if output_file is None and md_files:
        base_filename = os.path.splitext(os.path.basename(md_files[0]))[0]
        output_file = f"{base_filename}_Claude_HTML.html"
    else:
        output_file = 'merged_output.html'
        
    output_path = os.path.join(output_dir, output_file)
    if not md_files:
        print("No markdown files provided to merge! Exiting.")
        return
    
    for md_file in md_files:
        # Handle absolute paths and relative paths correctly
        if os.path.isabs(md_file):
            md_path = md_file
        else:
            # Check if the file exists directly in the specified directory
            direct_path = os.path.join(md_dir, md_file)
            if os.path.exists(direct_path):
                md_path = direct_path
            else:
                # Try with just the filename (in case path already includes directory)
                md_path = os.path.join(md_dir, os.path.basename(md_file))
        
        if not os.path.exists(md_path):
            print(f"Warning: {md_path} not found, skipping.")
            continue
        
        print(f"Processing: {md_path}")
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
                print("Enhancing content with Claude AI...")
                text = process_content_with_claude(text)
                print("Claude AI enhancement complete!")
            except Exception as e:
                print(f"Error using Claude API: {e}")
                print("Continuing without Claude processing...")
        
        # Use the 'tables' extension for proper table rendering
        html_content = markdown.markdown(text, extensions=['tables', 'attr_list'])
        section = f'<section>\n<h2>{os.path.splitext(os.path.basename(md_file))[0]}</h2>\n{html_content}\n</section>'
        merged_sections.append(section)
    
    section_content = '\n'.join(merged_sections)
    newline = '\n'
    html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Merged Markdown Documents</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
  <div class="container">
    {section_content}
  </div>
</body>
</html>'''
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
    print(f"Merged {len(merged_sections)} files into {output_path} with styling.")

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Convert markdown files to HTML using Claude AI')
    parser.add_argument('input_file', nargs='?', help='Input markdown file or document_order.json')
    parser.add_argument('--no-claude', action='store_true', help='Disable Claude API calls')
    parser.add_argument('--output', help='Output HTML file name')
    args = parser.parse_args()
    
    # Determine whether to use Claude
    use_claude = not args.no_claude
    
    # Check for NO_AI environment variable
    if os.environ.get('NO_AI'):
        use_claude = False
        print("Claude AI disabled by NO_AI environment variable.")
    
    if not use_claude:
        print("Claude API calls disabled. Running without processing.")
    
    # Handle input file
    if args.input_file:
        if args.input_file.endswith('.json'):
            # It's a document order file
            try:
                with open(args.input_file, 'r') as f:
                    order_data = json.load(f)
                
                # Extract filenames from the order data
                md_files = [item['filename'] for item in sorted(order_data, key=lambda x: x['order'])]
                
                convert_and_merge(md_files, output_file=args.output, use_claude=use_claude)
                print("Conversion completed successfully!")
            except Exception as e:
                print(f"Error processing JSON file: {e}")
                sys.exit(1)
        elif args.input_file.endswith('.md'):
            # It's a markdown file
            convert_and_merge([args.input_file], output_file=args.output, use_claude=use_claude)
            print("Conversion completed successfully!")
        else:
            print(f"Unsupported file type: {args.input_file}")
            sys.exit(1)
    else:
        # No input file specified, use document_order.json if it exists
        if os.path.exists('document_order.json'):
            try:
                with open('document_order.json', 'r') as f:
                    order_data = json.load(f)
                
                # Extract filenames from the order data
                md_files = [item['filename'] for item in sorted(order_data, key=lambda x: x['order'])]
                
                convert_and_merge(md_files, output_file=args.output, use_claude=use_claude)
                print("Conversion completed successfully!")
            except Exception as e:
                print(f"Error: {e}")
                sys.exit(1)
        else:
            # Process all markdown files in the directory
            md_dir = 'markdown'
            if not os.path.exists(md_dir):
                print(f"Error: '{md_dir}' directory not found!")
                sys.exit(1)
            
            md_files = [f for f in os.listdir(md_dir) if f.endswith('.md')]
            if not md_files:
                print("No markdown files found.")
                sys.exit(1)
            
            convert_and_merge(md_files, output_file=args.output, use_claude=use_claude)
            print("Conversion completed successfully!")
