# Check if Claude API key is set in .env file
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^ANTHROPIC_API_KEY=(.*)$') {
            $env:ANTHROPIC_API_KEY = $matches[1]
            Write-Host "Loaded Claude API key from .env file"
        }
    }
}

# If API key is not set, prompt the user
if (-not $env:ANTHROPIC_API_KEY) {
    Write-Host "Claude API key not found in .env file."
    Write-Host "Please create a .env file with your API key or set it manually:"
    Write-Host "$env:ANTHROPIC_API_KEY = \"your-api-key-here\""
}

# Check if format parameter is provided
param(
    [string]$format = "html",
    [string]$input = "input.md"
)

# Validate format
if ($format -ne "html" -and $format -ne "docx") {
    Write-Host "Invalid format. Please use 'html' or 'docx'."
    exit 1
}

# Run the appropriate converter
if ($format -eq "html") {
    python convert.py --input $input --output "output/${input}_Output.html" --model claude
} else {
    python convert.py --input $input --output "output/${input}_Output.docx" --model claude
}
