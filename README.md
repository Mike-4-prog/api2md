# api2md

API to Markdown documentation generator with change detection and AI-powered descriptions.

## Features

- Convert OpenAPI spec to Markdown documentation
- Compare two API versions and detect changes
- Validate OpenAPI specifications
- Output diff as JSON (for CI/CD) or Markdown (for PR comments)
- Generate AI-powered descriptions for new endpoints (using Ollama)

## Installation

```bash
git clone https://github.com/Mike-4-prog/api2md.git
cd api2md
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```
## Usage

```bash
# Generate documentation
python api2md.py --spec openapi.yaml --output docs/api.md

# Validate a spec
python api2md.py --spec openapi.yaml --validate

# Compare two API versions
python api2md.py --diff old.yaml new.yaml

# Compare with AI-generated descriptions
python api2md.py --diff old.yaml new.yaml --ai

# JSON output for CI/CD
python api2md.py --diff old.yaml new.yaml --json

# Markdown output for PR comments
python api2md.py --diff old.yaml new.yaml --markdown
```
## Requirements

- Python 3.8+
- Ollama (for AI features)

## License

MIT
