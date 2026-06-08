"""
Markdown Documentation Generator

Converts parsed OpenAPI specifications into clean, readable Markdown.
Supports table of contents, parameter tables, request/response examples, and schemas.
"""

import json
from pathlib import Path
from typing import Any
import click


class MarkdownGenerator:
    """
    Generate Markdown documentation from OpenAPI spec.
    
    Attributes:
        parser (OpenAPIParser): Parsed OpenAPI specification.
    """
    
    def __init__(self, parser):
        """Initialize generator with parsed OpenAPI spec."""
        self.parser = parser
    
    def _format_parameters(self, parameters: list) -> str:
        """
        Format parameters as a Markdown table.
        
        Args:
            parameters: List of parameter objects from OpenAPI spec.
        
        Returns:
            str: Markdown table representation of parameters.
        """
        if not parameters:
            return ""
        
        lines = ["| Name | In | Required | Description |"]
        lines.append("|------|----|----------|-------------|")
        
        for param in parameters:
            name = param.get('name', '')
            param_in = param.get('in', '')
            required = "Yes" if param.get('required') else "No"
            description = param.get('description', '')
            lines.append(f"| `{name}` | {param_in} | {required} | {description} |")
        
        return "\n".join(lines)
    
    def _create_anchor(self, method: str, path: str) -> str:
        """
        Create an HTML anchor ID from method and path for table of contents linking.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: API endpoint path.
        
        Returns:
            str: Sanitized anchor ID (e.g., "get-users-id").
        """
        anchor = f"{method.upper()}-{path.replace('/', '-').replace('{', '').replace('}', '')}".lower()
        anchor = anchor.replace('--', '-')
        return anchor
    
    def _format_schema(self, schema_name: str, schema: dict) -> str:
        """
        Format a single schema as Markdown with properties table.
        
        Args:
            schema_name: Name of the schema.
            schema: Schema definition object.
        
        Returns:
            str: Markdown representation of the schema.
        """
        lines = []
        lines.append(f"### {schema_name}\n")
        
        if schema.get('description'):
            lines.append(f"{schema['description']}\n")
        
        schema_type = schema.get('type', 'object')
        lines.append(f"**Type:** `{schema_type}`\n")
        
        if schema.get('required'):
            required_fields = ", ".join([f"`{f}`" for f in schema['required']])
            lines.append(f"**Required Fields:** {required_fields}\n")
        
        if schema.get('properties'):
            lines.append("**Properties:**\n")
            lines.append("| Name | Type | Required | Description | Example |")
            lines.append("|------|------|----------|-------------|---------|")
            
            for prop_name, prop_details in schema['properties'].items():
                prop_type = prop_details.get('type', 'string')
                is_required = "Yes" if prop_name in schema.get('required', []) else "No"
                description = prop_details.get('description', '')
                example = prop_details.get('example', '')
                
                # Handle references and arrays
                if prop_details.get('$ref'):
                    prop_type = f"`{prop_details['$ref'].split('/')[-1]}`"
                elif prop_details.get('type') == 'array':
                    items = prop_details.get('items', {})
                    if items.get('$ref'):
                        prop_type = f"array of `{items['$ref'].split('/')[-1]}`"
                    else:
                        prop_type = f"array of {items.get('type', 'string')}"
                
                lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {description} | `{example}` |")
        
        if schema.get('example'):
            example = json.dumps(schema['example'], indent=2)
            lines.append(f"\n**Example:**\n```json\n{example}\n```")
        
        lines.append("")
        return "\n".join(lines)
    
    def generate(self, output_path: str) -> None:
        """
        Generate complete Markdown documentation and write to file.
        
        Args:
            output_path: Path where the Markdown file will be written.
        """
        lines = []
        
        # API header
        info = self.parser.get_info()
        lines.append(f"# {info.get('title', 'API Documentation')}\n")
        lines.append(f"**Version:** {info.get('version', 'N/A')}\n")
        
        if info.get('description'):
            lines.append(f"{info['description']}\n")
        
        lines.append("---\n")
        lines.append("## Endpoints\n")
        
        # Table of Contents
        lines.append("### Table of Contents\n")
        paths = self.parser.get_paths()
        for path, methods in paths.items():
            for method in methods.keys():
                if method.lower() in ['get', 'post', 'put', 'delete', 'patch']:
                    anchor = self._create_anchor(method, path)
                    lines.append(f"- [{method.upper()} {path}](#{anchor})")
        lines.append("\n---\n")
        
        # Detailed endpoint documentation
        for path, methods in paths.items():
            for method, details in methods.items():
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    continue
                
                anchor = self._create_anchor(method, path)
                lines.append(f"<a id='{anchor}'></a>\n")
                lines.append(f"### `{method.upper()}` `{path}`\n")
                
                if details.get('summary'):
                    lines.append(f"**Summary:** {details['summary']}\n")
                
                if details.get('description'):
                    lines.append(f"{details['description']}\n")
                
                # Parameters
                if details.get('parameters'):
                    lines.append("**Parameters:**\n")
                    lines.append(self._format_parameters(details['parameters']))
                    lines.append("")
                
                # Request Body
                if details.get('requestBody'):
                    lines.append("**Request Body:**\n")
                    content = details['requestBody'].get('content', {})
                    for content_type, schema_info in content.items():
                        lines.append(f"- **Content-Type:** `{content_type}`")
                        
                        if 'schema' in schema_info:
                            schema = schema_info['schema']
                            schema_type = schema.get('type', 'object')
                            lines.append(f"- **Schema Type:** `{schema_type}`")
                            
                            if 'required' in schema:
                                required_fields = ", ".join(schema['required'])
                                lines.append(f"- **Required Fields:** `{required_fields}`")
                            
                            # Generate example from schema
                            if 'example' in schema:
                                example = json.dumps(schema['example'], indent=2)
                                lines.append(f"\n**Example:**\n```json\n{example}\n```")
                            elif 'properties' in schema:
                                example_obj = {}
                                for prop_name, prop_details in schema['properties'].items():
                                    prop_type = prop_details.get('type', 'string')
                                    if prop_type == 'string':
                                        example_obj[prop_name] = f"<{prop_name}>"
                                    elif prop_type == 'integer':
                                        example_obj[prop_name] = 0
                                    elif prop_type == 'boolean':
                                        example_obj[prop_name] = True
                                    else:
                                        example_obj[prop_name] = None
                                example = json.dumps(example_obj, indent=2)
                                lines.append(f"\n**Example:**\n```json\n{example}\n```")
                    lines.append("")
                
                # Responses
                if details.get('responses'):
                    lines.append("**Responses:**\n")
                    for status_code, response in details['responses'].items():
                        description = response.get('description', '')
                        lines.append(f"- **{status_code}:** {description}")
                    lines.append("")
                
                lines.append("---\n")
        
        # Schemas section
        components = self.parser.get_components()
        schemas = components.get('schemas', {})
        
        if schemas:
            lines.append("## Schemas\n")
            lines.append("Reusable data models used throughout this API.\n")
            
            for schema_name, schema in schemas.items():
                lines.append(self._format_schema(schema_name, schema))
                lines.append("---\n")
        
        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(lines), encoding='utf-8')
        click.echo(f"[OK] Documentation written to {output_path}")