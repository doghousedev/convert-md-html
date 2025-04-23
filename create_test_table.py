import markdown
from bs4 import BeautifulSoup

# Create a markdown table
md_content = """
# Test Table

| Manufacturer | Model | Description | Quantity | Unit Price | Extended Price |
|-------------|-------|-------------|----------|------------|----------------|
| CONTEMP. RESEARCH | 232-ATSC 4K HDTV TUNER | ATSC Tuner | 1 | $1,006.88 | $1,006.88 |
| CRESTRON | AM-3100-WF | Wireless Video Receiver | 1 | $1,406.25 | $1,406.25 |
| CRESTRON | AM-TX3-100 | Wireless Video Transmitter | 2 | $1,040.63 | $2,081.26 |
| LG | 86UH5J-H | Large Format Display | 1 | $5,463.75 | $5,463.75 |
| LG | 32SM5J-B | Small Format Display | 2 | $705.00 | $1,410.00 |
| LOGITECH | RALLY (960-001226) | Camera | 1 | $1,595.85 | $1,595.85 |
| QSC | NV-32-H | AVC Processor | 1 | $3,297.05 | $3,297.05 |
| QSC | NV-21-HU | AVoIP Decoder | 3 | $1,955.79 | $5,867.37 |
| VADDIO | 999-1005-032 | USB 3.0 Extender Kit (TX/RX Pair) | 1 | $1,740.38 | $1,740.38 |
| YODECK | OFE | OFE Digital Signage Player | 1 | $0.00 | $0.00 |
| Subtotal | | | | | $23,868.79 |
"""

# Convert markdown to HTML
html_content = markdown.markdown(md_content, extensions=['tables'])

# Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Style the table
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
            header['style'] = 'background-color: #343a40; color: white; padding: 8px; vertical-align: middle;'
    
    # Style the table cells
    for row in table.find_all('tr'):
        for cell in row.find_all(['td', 'th']):
            if cell.name == 'td':
                cell['style'] = 'padding: 8px; vertical-align: middle;'

# Create a complete HTML document
html_template = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Table Test</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css">
    <style>
        body {{ padding: 20px; }}
        .container {{ max-width: 1200px; }}
    </style>
</head>
<body>
    <div class="container">
        {soup}
    </div>
</body>
</html>
'''

# Write the HTML to a file
with open('test_table_output.html', 'w', encoding='utf-8') as f:
    f.write(html_template)

print("HTML file created: test_table_output.html")
