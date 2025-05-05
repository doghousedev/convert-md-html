#!/usr/bin/env python
"""
Markdown Converter

This script allows you to convert Markdown files to HTML or DOCX
using either OpenAI or Claude for text enhancement.

Usage:
  python convert.py [options]

Options:
  --format, -f    Output format: html or docx (default: html)
  --model, -m     AI model: openai or claude (default: claude)
  --no-ai         Disable AI processing
  --input, -i     Input file or directory (default: uses document_order.json)
  --output, -o    Output file (default: based on input filename)
  --help, -h      Show this help message
"""

import os
import sys
import argparse
import json
from pathlib import Path
import subprocess
import time

# Set up argument parser
parser = argparse.ArgumentParser(description="Convert Markdown to HTML or DOCX using AI")
parser.add_argument("--format", "-f", choices=["html", "docx"], default="html",
                    help="Output format: html or docx (default: html)")
parser.add_argument("--model", "-m", choices=["openai", "claude"], default="claude",
                    help="AI model to use: openai or claude (default: claude)")
parser.add_argument("--no-ai", action="store_true",
                    help="Disable AI processing")
parser.add_argument("--input", "-i", type=str,
                    help="Input file or directory (default: uses document_order.json)")
parser.add_argument("--output", "-o", type=str,
                    help="Output file (default: based on input filename)")
parser.add_argument("--log", action="store_true",
                    help="Enable detailed logging of AI responses")

# Check if API keys are available
def check_api_keys():
    api_keys = {}
    
    # Try to load from .env file first
    try:
        from dotenv import load_dotenv
        # Construct path to .env file in the project root
        dotenv_path = Path(__file__).parent / '.env' 
        # Force reload to ensure we get the latest values
        load_dotenv(dotenv_path=dotenv_path, override=True)
    except ImportError:
        print("Warning: python-dotenv not installed. Using environment variables only.")
    except Exception as e:
        print(f"Error loading .env file: {e}")
    
    # Get API keys from environment variables (which now include any from .env)
    openai_key = os.environ.get('OPENAI_API_KEY')
    claude_key = os.environ.get('ANTHROPIC_API_KEY')
    
    # Debug output (masked for security)
    if openai_key:
        print(f"OpenAI API key found: {openai_key[:5]}...{openai_key[-5:]}")
    else:
        print("OpenAI API key not found")
        
    if claude_key:
        print(f"Claude API key found: {claude_key[:5]}...{claude_key[-5:]}")
    else:
        print("Claude API key not found")
    
    api_keys['openai'] = openai_key
    api_keys['claude'] = claude_key
    return api_keys

def main():
    args = parser.parse_args()
    
    # Set environment variables for API keys
    api_keys = check_api_keys()
    
    # Clear any previous NO_AI setting
    if 'NO_AI' in os.environ:
        del os.environ['NO_AI']
    
    # Determine which script to run
    if args.format == "html":
        if args.model == "claude" and not args.no_ai:
            if not api_keys['claude']:
                print("Warning: No Claude API key found. Running without AI processing.")
                script = "converters/md_to_html.py"
                os.environ["NO_AI"] = "1"
            else:
                script = "converters/md_to_html_claude.py"
                os.environ["ANTHROPIC_API_KEY"] = api_keys['claude']
                # Make sure NO_AI is not set
                if 'NO_AI' in os.environ:
                    del os.environ['NO_AI']
        else:  # openai or no-ai
            script = "converters/md_to_html.py"
            if args.no_ai:
                os.environ["NO_AI"] = "1"
                print("AI processing disabled by user")
            elif api_keys['openai']:
                os.environ["OPENAI_API_KEY"] = api_keys['openai']
                # Make sure NO_AI is not set
                if 'NO_AI' in os.environ:
                    del os.environ['NO_AI']
                print("AI processing enabled with OpenAI")
            else:
                print("Warning: No OpenAI API key found. Running without AI processing.")
                os.environ["NO_AI"] = "1"
    else:  # docx
        if args.model == "claude" and not args.no_ai:
            if not api_keys['claude']:
                print("Warning: No Claude API key found. Running without AI processing.")
                script = "converters/md_to_docx.py"
                os.environ["NO_AI"] = "1"
            else:
                script = "converters/md_to_docx_claude.py"
                os.environ["ANTHROPIC_API_KEY"] = api_keys['claude']
                # Make sure NO_AI is not set
                if 'NO_AI' in os.environ:
                    del os.environ['NO_AI']
        else:  # openai or no-ai
            script = "converters/md_to_docx.py"
            if args.no_ai:
                os.environ["NO_AI"] = "1"
                print("AI processing disabled by user")
            elif api_keys['openai']:
                os.environ["OPENAI_API_KEY"] = api_keys['openai']
                # Make sure NO_AI is not set
                if 'NO_AI' in os.environ:
                    del os.environ['NO_AI']
                print("AI processing enabled with OpenAI")
            else:
                print("Warning: No OpenAI API key found. Running without AI processing.")
                os.environ["NO_AI"] = "1"
    
    # Build command
    cmd = [sys.executable, script]
    
    # Add input file if specified
    if args.input:
        cmd.append(args.input)
    
    # Add output file if specified
    # Check the script type to pass output correctly
    if args.output:
        if "md_to_html_claude.py" in script or "md_to_docx_claude.py" in script: 
            cmd.extend(["--output", args.output])
        else: 
            cmd.append(args.output)
    
    # Add no-ai flag if specified
    if args.no_ai:
        if "claude" in script:
            cmd.append("--no-claude")
        else:
            cmd.append("--no-openai")
            
    # Add logging flag if specified
    if args.log:
        cmd.append("--log")
        print("Detailed AI response logging enabled")
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    start_time = time.time()
    try:
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        elapsed_time = time.time() - start_time
        print(f"\nConversion completed successfully in {elapsed_time:.2f} seconds!")
        
        # Print output directory information
        output_dir = os.path.join(os.getcwd(), 'output')
        if os.path.exists(output_dir):
            files = os.listdir(output_dir)
            if files:
                print(f"Output files available in: {output_dir}")
                for file in files:
                    if file.endswith('.docx') or file.endswith('.html'):
                        print(f"  - {file}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with exit code {e.returncode}")
        if e.stdout:
            print("\nCommand output:\n", e.stdout)
        if e.stderr:
            print("\nError details:\n", e.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: Could not find the required file or command: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
