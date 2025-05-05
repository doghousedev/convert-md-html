# Changelog

All notable changes to this project will be documented in this file.

## [1.1.2] - 2025-05-05

### Added
- Added new Claude API integration fixed version
- New markdown templates for various document types

### Improved
- Enhanced HTML conversion with better formatting
- Updated document templates for more consistent output
- Refined JSON configuration for better document ordering

### Fixed
- Fixed issues with Claude API integration
- Removed redundant template file

## [1.1.1] - 2025-04-23

### Added
- Detailed AI response logging to a single file per run
- Command-line option (--log) to enable AI response logging

### Improved
- Enhanced table handling in both HTML and DOCX output with proper formatting
- Better detection and rendering of pipe-separated tables
- Proper handling of table headers and separator rows
- Bootstrap styling for HTML tables with dark headers and striped rows
- Consistent table formatting in DOCX with proper headers and cell formatting

### Removed
- Unnecessary test files and scripts
- Redundant markdown test files

## [1.1.0] - 2025-04-22

### Added
- Word document (.docx) output support
- Ability to use Word templates for consistent formatting
- Improved HTML-to-Word conversion with formatting preservation
- Command-line option to specify a Word template file
- Dynamic output filenames based on input filename (e.g., input.md → input_Output.html/docx)

### Changed
- Updated requirements.txt to include python-docx dependency

## [1.0.0] - 2025-04-22

### Added
- Initial release of the Markdown to HTML converter
- Support for converting multiple markdown files to a single HTML document
- OpenAI integration for paraphrasing bullet points into paragraphs
- JSON-based ordering system for controlling the sequence of markdown files
- Basic styling with CSS
- Netlify deployment configuration

### Changed
- N/A (Initial release)

### Fixed
- Fixed f-string syntax error with newline characters
- Updated OpenAI API key handling to support project-scoped keys
