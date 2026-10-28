# api2md

Keeping API docs in sync with code is hard. api2md converts OpenAPI specs to Markdown, detects changes between versions, and generates AI-powered descriptions for new endpoints.

> **Runs in your CI. No SaaS, no dashboard, no data leaves your repo. One YAML file, MIT licensed.**

## The Problem

API docs rot. When a spec changes, the docs lag behind. Developers get confused, support tickets pile up, and the documentation becomes a liability instead of an asset.

api2md solves this by:
1. Converting OpenAPI specs to clean Markdown.
2. Diffing two versions to show exactly what changed.
3. Outputting JSON for CI/CD gates or Markdown for PR comments.

## Tested Against Real-World Specs

This is not a tutorial project. It handles the hardest specs in the industry.

| Spec | Version | Size | Endpoints | Validation Errors | Raw \ Leaks |
|------|---------|------|-----------|-------------------|-----------------|
| GitHub API | OpenAPI 3.x | 13 MB | 900+ | 0 | 0 |
| Stripe API | OpenAPI 3.x | 8.3 MB | 500+ | 0 | 0 |
| Kubernetes API | Swagger 2.0 | 4.4 MB | 1,000+ | 0 | 0 |

## Quick Test (Under 5 Minutes)

~~~bash
# Clone the repository
git clone https://github.com/Mike-4-prog/api2md.git
cd api2md

# Set up environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Validate a sample spec
python api2md.py --spec sample.yaml --validate

# Generate documentation
python api2md.py --spec sample.yaml --output docs/sample.md

# Diff two versions
python api2md.py --diff old.yaml new.yaml
~~~

## Use as a GitHub Action

You can use `api2md` directly in your GitHub workflows to automatically validate and generate docs whenever your API spec changes.

```yaml
name: Generate API Docs

on:
  push:
    branches: [ main ]

jobs:
  api2md:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run api2md
        uses: Mike-4-prog/api2md@main
        with:
          spec: 'openapi.yaml'
          output: 'docs/API.md'
          validate: 'true'
          
      - name: Commit generated docs
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add docs/API.md
          git commit -m "docs: auto-generate API documentation" || exit 0
          git push
```

## Features

- **OpenAPI 3.x and Swagger 2.0 support** (JSON and YAML)
- **\ resolution** for parameters, request bodies, and schemas
- **Composition handling** (allOf, anyOf, oneOf)
- **Version diffing** across endpoints, methods, parameters, and schemas
- **JSON output** for CI/CD pipelines
- **Response schema rendering** as Markdown tables
- **Markdown output** for PR comments
- **AI-powered descriptions** using Ollama

## How It Works

1. **Parse:** Loads the OpenAPI spec (JSON or YAML).
2. **Validate:** Checks the spec for errors and resolves \.
3. **Generate:** Converts the spec to Markdown documentation.
4. **Diff:** Compares two versions and outputs changes in text, JSON, or Markdown.

## Requirements

- Python 3.8+
- Ollama (for AI features only)

## License

MIT
