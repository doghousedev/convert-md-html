import os
import sys
from converters.md_to_html import convert_md_to_html

# Test the HTML converter directly
input_file = 'markdown/Bomark_BSO_av-proposal.md'
output_file = 'output/Bomark_BSO_av-proposal_Output.html'

# Ensure output directory exists
if not os.path.exists('output'):
    os.makedirs('output')

print(f"Converting {input_file} to {output_file}")
result = convert_md_to_html(input_file, output_file)
print(f"Result: {result}")

# Check if the file was created
if os.path.exists(output_file):
    print(f"Success! File created: {output_file} ({os.path.getsize(output_file)} bytes)")
else:
    print(f"Error: File not created: {output_file}")
