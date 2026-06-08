#!/usr/bin/env python3
"""
API to Markdown Documentation Generator

A CLI tool that converts OpenAPI specifications to Markdown documentation,
detects changes between API versions, validates spec structure, and generates
AI-powered descriptions for new endpoints using local LLMs (Ollama).
"""

import click
from typing import Optional

from core.parser import OpenAPIParser
from core.validator import OpenAPIValidator
from core.generator import MarkdownGenerator
from core.differ import OpenAPIDiffer
from ai.ollama import generate_description_for_endpoint


@click.command()
@click.option('--spec', '-s', help='Path to OpenAPI spec file (JSON or YAML)')
@click.option('--output', '-o', default='./docs/api.md', 
              help='Output path for Markdown file (default: ./docs/api.md)')
@click.option('--diff', '-d', nargs=2, metavar='<old-spec> <new-spec>', 
              help='Compare two OpenAPI specs')
@click.option('--json', 'json_output', is_flag=True, 
              help='Output diff as JSON (only with --diff)')
@click.option('--markdown', 'markdown_output', is_flag=True, 
              help='Output diff as Markdown (only with --diff)')
@click.option('--validate', '-v', is_flag=True, 
              help='Validate OpenAPI spec (requires --spec)')
@click.option('--ai', is_flag=True, 
              help='Use AI to generate descriptions for new items (requires Ollama)')
def main(
    spec: Optional[str],
    output: str,
    diff: Optional[tuple],
    json_output: bool,
    markdown_output: bool,
    validate: bool,
    ai: bool
) -> None:
    """Generate Markdown documentation or compare OpenAPI specs."""
    
    # Validation mode
    if validate:
        if not spec:
            click.echo("ERROR: --validate requires --spec", err=True)
            raise click.Abort()
        
        click.echo(f"Validating OpenAPI spec: {spec}\n")
        try:
            validator = OpenAPIValidator(spec)
            validator.validate()
            click.echo(validator.get_report())
            if validator.errors:
                raise click.Abort()
        except Exception as e:
            if "Aborted" not in str(e):
                click.echo(f"Error during validation: {e}", err=True)
            raise click.Abort()
        return
    
    # Diff mode
    if diff:
        old_file, new_file = diff
        
        if json_output:
            click.echo(f"Comparing OpenAPI specs (JSON output):\n   Old: {old_file}\n   New: {new_file}\n", err=True)
        elif markdown_output:
            click.echo(f"Comparing OpenAPI specs (Markdown output):\n   Old: {old_file}\n   New: {new_file}\n", err=True)
        else:
            click.echo(f"Comparing OpenAPI specs:\n   Old: {old_file}\n   New: {new_file}\n")
        
        try:
            differ = OpenAPIDiffer(old_file, new_file)
            
            if json_output:
                click.echo(differ.generate_json_report())
            elif markdown_output:
                click.echo(differ.generate_report(format='markdown'))
            else:
                click.echo(differ.generate_report(format='text'))
            
            # AI-generated descriptions
            if ai:
                click.echo("\n" + "=" * 60)
                click.echo("AI-Generated Descriptions")
                click.echo("=" * 60)
                
                for path in differ.detect_added_paths():
                    desc = generate_description_for_endpoint("", path)
                    click.echo(f"\nNew endpoint: {path}")
                    click.echo(f"   Suggested description: {desc}")
                
                for path, method in differ.detect_added_methods():
                    desc = generate_description_for_endpoint(method, path)
                    click.echo(f"\nNew method: {method.upper()} {path}")
                    click.echo(f"   Suggested description: {desc}")
            
            click.echo("\nDiff complete!", err=True)
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            raise click.Abort()
        return
    
    # Generate mode
    if not spec:
        click.echo("ERROR: Please provide --spec or --diff or --validate", err=True)
        click.echo("\nUsage:")
        click.echo("  Generate docs: api2md --spec openapi.yaml --output docs/api.md")
        click.echo("  Validate spec: api2md --spec openapi.yaml --validate")
        click.echo("  Compare specs: api2md --diff old.yaml new.yaml")
        click.echo("  Compare specs (JSON): api2md --diff old.yaml new.yaml --json")
        click.echo("  Compare specs (Markdown): api2md --diff old.yaml new.yaml --markdown")
        click.echo("  Compare specs with AI: api2md --diff old.yaml new.yaml --ai")
        raise click.Abort()
    
    click.echo("API to Markdown Generator\n")
    
    try:
        parser = OpenAPIParser(spec)
        generator = MarkdownGenerator(parser)
        generator.generate(output)
        click.echo("\nDone!")
    except Exception as e:
        click.echo(f"\nFailed: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()