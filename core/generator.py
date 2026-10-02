"""
Markdown Documentation Generator

Converts parsed OpenAPI specifications into clean, readable Markdown.
Supports table of contents, parameter tables, request/response examples, and schemas.
Supports $ref resolution for parameters, request bodies, and schemas.
Renders nested object schemas as links with property counts.
Handles anyOf, oneOf, allOf composition at property level.
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
    
    def _resolve_ref(self, ref: str) -> Any:
        """
        Resolve a $ref string to the object it points to.
        
        Handles:
        - #/components/schemas/<name>
        - #/components/parameters/<name>
        - #/components/requestBodies/<name>
        - #/components/responses/<name>
        
        Args:
            ref: Reference string, e.g. '#/components/parameters/owner'.
        
        Returns:
            The resolved object dict, or None if not found.
        """
        if not ref or not isinstance(ref, str) or not ref.startswith('#/'):
            return None
        parts = ref.lstrip('#/').split('/')
        if len(parts) < 3 or parts[0] != 'components':
            return None
        category = parts[1]
        name = parts[2]
        components = self.parser.get_components()
        category_dict = components.get(category, {})
        return category_dict.get(name)
    
    def _describe_type(self, prop_details: dict) -> str:
        """
        Build a human-readable type string for a schema property.
        
        Handles $ref (as link), arrays (with item type), objects (with property count),
        anyOf/oneOf/allOf composition, and primitive types.
        
        Args:
            prop_details: Schema property definition dict.
        
        Returns:
            str: Markdown-safe type description.
        """
        # $ref directly
        if prop_details.get('$ref'):
            name = prop_details['$ref'].split('/')[-1]
            return f"[`{name}`](#{name.lower()})"
        
        # Composition: anyOf, oneOf, allOf at property level
        for keyword in ('anyOf', 'oneOf', 'allOf'):
            if keyword in prop_details:
                variants = prop_details[keyword]
                labels = []
                for variant in variants:
                    if isinstance(variant, dict) and variant.get('$ref'):
                        vname = variant['$ref'].split('/')[-1]
                        labels.append(f"[`{vname}`](#{vname.lower()})")
                    elif isinstance(variant, dict) and variant.get('type'):
                        labels.append(variant['type'])
                if labels:
                    keyword_label = {
                        'anyOf': 'any of',
                        'oneOf': 'one of',
                        'allOf': 'all of'
                    }[keyword]
                    return f"{keyword_label}: " + ", ".join(labels)
                return keyword
        
        prop_type = prop_details.get('type', 'string')
        
        # Array: describe item type
        if prop_type == 'array':
            items = prop_details.get('items', {})
            if items.get('$ref'):
                item_name = items['$ref'].split('/')[-1]
                return f"array of [`{item_name}`](#{item_name.lower()})"
            elif items.get('type') == 'object' and items.get('properties'):
                return f"array of object ({len(items['properties'])} props)"
            else:
                return f"array of {items.get('type', 'string')}"
        
        # Object: show property count if inline properties exist
        if prop_type == 'object':
            inline_props = prop_details.get('properties', {})
            if inline_props:
                return f"object ({len(inline_props)} props)"
            return "object"
        
        # Primitive
        return prop_type
    
    def _format_parameters(self, parameters: list) -> str:
        """
        Format parameters as a Markdown table.
        Resolves $ref parameters before reading name and location.
        
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
            # Resolve if $ref
            if isinstance(param, dict) and param.get('$ref'):
                resolved = self._resolve_ref(param['$ref'])
                if not isinstance(resolved, dict):
                    continue
                param = resolved
            
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
        lines.append(f"<a id='{schema_name.lower()}'></a>\n")
        lines.append(f"### {schema_name}\n")
        
        if schema.get('description'):
            lines.append(f"{schema['description']}\n")
        
        # Handle allOf composition (merge properties)
        merged = self._merge_composition(schema)
        
        schema_type = merged.get('type', 'object')
        lines.append(f"**Type:** `{schema_type}`\n")
        
        if merged.get('required'):
            required_fields = ", ".join([f"`{f}`" for f in merged['required']])
            lines.append(f"**Required Fields:** {required_fields}\n")
        
        if merged.get('properties'):
            lines.append("**Properties:**\n")
            lines.append("| Name | Type | Required | Description | Example |")
            lines.append("|------|------|----------|-------------|---------|")
            
            for prop_name, prop_details in merged['properties'].items():
                prop_type = self._describe_type(prop_details)
                is_required = "Yes" if prop_name in merged.get('required', []) else "No"
                description = prop_details.get('description', '')
                example = prop_details.get('example', '')
                lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {description} | `{example}` |")
        
        if schema.get('example'):
            example = json.dumps(schema['example'], indent=2)
            lines.append(f"\n**Example:**\n```json\n{example}\n```")
        
        lines.append("")
        return "\n".join(lines)
    
    def _merge_composition(self, schema: dict) -> dict:
        """
        Merge allOf composition into a single flat schema dict.
        Handles nested $ref inside allOf.
        
        Args:
            schema: Schema dict possibly containing allOf.
        
        Returns:
            dict: Merged schema with combined properties and required fields.
        """
        if not isinstance(schema, dict):
            return schema
        
        if 'allOf' not in schema:
            return schema
        
        merged = {
            'type': schema.get('type', 'object'),
            'properties': {},
            'required': []
        }
        
        for part in schema['allOf']:
            # Resolve $ref if present
            if isinstance(part, dict) and part.get('$ref'):
                resolved = self._resolve_ref(part['$ref'])
                if isinstance(resolved, dict):
                    part = resolved
                else:
                    continue
            
            if not isinstance(part, dict):
                continue
            
            # Recursively merge nested allOf
            part = self._merge_composition(part)
            
            # Merge properties
            for prop_name, prop_details in part.get('properties', {}).items():
                merged['properties'][prop_name] = prop_details
            
            # Merge required
            merged['required'].extend(part.get('required', []))
        
        # Also merge top-level properties if any
        for prop_name, prop_details in schema.get('properties', {}).items():
            merged['properties'][prop_name] = prop_details
        merged['required'].extend(schema.get('required', []))
        
        # Deduplicate required
        merged['required'] = list(dict.fromkeys(merged['required']))
        
        return merged
    
    def _build_example_from_schema(self, schema: dict) -> Any:
        """
        Build a placeholder example object from a schema definition.
        
        Args:
            schema: Schema definition (with properties).
        
        Returns:
            A dict representing an example payload, or None.
        """
        if not schema or 'properties' not in schema:
            return None
        example_obj = {}
        for prop_name, prop_details in schema['properties'].items():
            prop_type = prop_details.get('type', 'string')
            if prop_details.get('$ref'):
                ref_name = prop_details['$ref'].split('/')[-1]
                resolved = self._resolve_ref(prop_details['$ref'])
                if resolved:
                    example_obj[prop_name] = self._build_example_from_schema(resolved)
                else:
                    example_obj[prop_name] = f"<{ref_name}>"
            elif prop_type == 'string':
                example_obj[prop_name] = f"<{prop_name}>"
            elif prop_type == 'integer':
                example_obj[prop_name] = 0
            elif prop_type == 'number':
                example_obj[prop_name] = 0.0
            elif prop_type == 'boolean':
                example_obj[prop_name] = True
            elif prop_type == 'array':
                items = prop_details.get('items', {})
                if items.get('$ref'):
                    resolved = self._resolve_ref(items['$ref'])
                    if resolved:
                        example_obj[prop_name] = [self._build_example_from_schema(resolved)]
                    else:
                        example_obj[prop_name] = []
                else:
                    example_obj[prop_name] = []
            elif prop_type == 'object':
                inline_props = prop_details.get('properties', {})
                if inline_props:
                    example_obj[prop_name] = self._build_example_from_schema({'properties': inline_props})
                else:
                    example_obj[prop_name] = {}
            else:
                example_obj[prop_name] = None
        return example_obj
    
    def _format_properties_table(self, properties: dict, required: list) -> list:
        """
        Build a properties table as a list of lines.
        
        Args:
            properties: Dict of property name -> details.
            required: List of required property names.
        
        Returns:
            list of markdown lines.
        """
        lines = []
        lines.append("| Field | Type | Required | Description |")
        lines.append("|-------|------|----------|-------------|")
        for prop_name, prop_details in properties.items():
            prop_type = self._describe_type(prop_details)
            is_required = "Yes" if prop_name in required else "No"
            description = prop_details.get('description', '')
            lines.append(f"| `{prop_name}` | {prop_type} | {is_required} | {description} |")
        return lines
    
    def _format_request_body(self, request_body: dict) -> str:
        """
        Format a request body section, resolving $ref to schemas.
        Handles allOf composition.
        
        Args:
            request_body: The requestBody object from the OpenAPI spec.
        
        Returns:
            str: Markdown representation.
        """
        lines = []
        
        # Resolve requestBody itself if it is a $ref
        if isinstance(request_body, dict) and request_body.get('$ref'):
            resolved_body = self._resolve_ref(request_body['$ref'])
            if isinstance(resolved_body, dict):
                request_body = resolved_body
        
        content = request_body.get('content', {})
        
        for content_type, schema_info in content.items():
            lines.append(f"- **Content-Type:** `{content_type}`")
            
            if 'schema' not in schema_info:
                continue
            
            schema = schema_info['schema']
            
            # Handle $ref first (before merging composition)
            if isinstance(schema, dict) and schema.get('$ref'):
                ref_name = schema['$ref'].split('/')[-1]
                lines.append(f"- **Schema:** [`{ref_name}`](#{ref_name.lower()})")
                
                resolved = self._resolve_ref(schema['$ref'])
                if resolved:
                    resolved = self._merge_composition(resolved)
                    if resolved.get('required'):
                        required_fields = ", ".join([f"`{f}`" for f in resolved['required']])
                        lines.append(f"- **Required Fields:** {required_fields}")
                    
                    if resolved.get('properties'):
                        lines.append("")
                        lines.extend(self._format_properties_table(
                            resolved['properties'], resolved.get('required', [])
                        ))
                    
                    example_obj = self._build_example_from_schema(resolved)
                    if example_obj:
                        example = json.dumps(example_obj, indent=2)
                        lines.append("")
                        lines.append(f"**Example:**\n```json\n{example}\n```")
                else:
                    lines.append(f"  (Schema `{ref_name}` not found in components)")
                continue
            
            # Merge allOf composition if present
            schema = self._merge_composition(schema)
            
            # Inline schema
            schema_type = schema.get('type', 'object')
            lines.append(f"- **Schema Type:** `{schema_type}`")
            
            if schema.get('required'):
                required_fields = ", ".join(schema['required'])
                lines.append(f"- **Required Fields:** `{required_fields}`")
            
            if schema.get('properties'):
                lines.append("")
                lines.extend(self._format_properties_table(
                    schema['properties'], schema.get('required', [])
                ))
            
            if schema.get('example'):
                example = json.dumps(schema['example'], indent=2)
                lines.append("")
                lines.append(f"**Example:**\n```json\n{example}\n```")
            elif schema.get('properties'):
                example_obj = self._build_example_from_schema(schema)
                if example_obj:
                    example = json.dumps(example_obj, indent=2)
                    lines.append("")
                    lines.append(f"**Example:**\n```json\n{example}\n```")
        
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
                    lines.append(self._format_request_body(details['requestBody']))
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