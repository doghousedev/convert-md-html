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

# Check if API keys are available
def check_api_keys():
    api_keys = {}
    
    # Try to load from .env file first
    try:
        from dotenv import load_dotenv
        # Force reload to ensure we get the latest values
        load_dotenv(override=True)
        print("Loaded API keys from .env file")
    except ImportError:
        print("Warning: python-dotenv not installed. Using environment variables only.")
    
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
        else:  # openai or no-ai
            script = "converters/md_to_html.py"
            if args.no_ai:
                os.environ["NO_AI"] = "1"
            elif api_keys['openai']:
                os.environ["OPENAI_API_KEY"] = api_keys['openai']
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
        else:  # openai or no-ai
            script = "converters/md_to_docx.py"
            if args.no_ai:
                os.environ["NO_AI"] = "1"
            elif api_keys['openai']:
                os.environ["OPENAI_API_KEY"] = api_keys['openai']
            else:
                print("Warning: No OpenAI API key found. Running without AI processing.")
                os.environ["NO_AI"] = "1"
    
    # Build command
    cmd = [sys.executable, script]
    
    # Add input file if specified
    if args.input:
        cmd.append(args.input)
    
    # Add output file if specified
    if args.output:
        cmd.append(args.output)
    
    # Add no-ai flag if specified
    if args.no_ai:
        if "claude" in script:
            cmd.append("--no-claude")
        else:
            cmd.append("--no-openai")
    
    # Run the command
    print(f"Running: {' '.join(cmd)}")
    start_time = time.time()
    try:
        subprocess.run(cmd, check=True)
        elapsed_time = time.time() - start_time
        print(f"\nConversion completed successfully in {elapsed_time:.2f} seconds!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
