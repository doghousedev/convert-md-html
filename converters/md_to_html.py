import os
import re
import markdown
import openai
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
        # For OpenAI 0.28.0
        client = openai.Client(api_key=OPENAI_API_KEY)
        print("Using OpenAI API v0.28.0")
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("Falling back to no AI mode")
        os.environ["NO_AI"] = "1"

def convert_md_to_html(input_file, output_file=None, document_order_file=None):
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
    
    # Process tables
    for table in soup.find_all('table'):
        table['class'] = 'table table-bordered'
    
    # Process bullet lists
    for ul in soup.find_all('ul'):
        ul['class'] = 'list-group'
        for li in ul.find_all('li'):
            li['class'] = 'list-group-item'
    
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
    
    # Write the HTML to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print(f"Conversion complete. Output saved to {output_file}")
    return output_file
