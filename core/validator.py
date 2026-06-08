"""
OpenAPI Specification Validator

Validates OpenAPI spec files for structural correctness.
Detects missing required fields, invalid HTTP methods, parameter issues, etc.
"""

import yaml
import json
from typing import Dict, Any
import click


class OpenAPIValidator:
    """
    Validate OpenAPI specification structure.
    
    Attributes:
        spec_path (str): Path to the spec file.
        spec (dict): Loaded specification.
        errors (list): Critical validation errors.
        warnings (list): Non-critical issues.
    """
    
    def __init__(self, spec_path: str):
        """Initialize validator and load spec."""
        self.spec_path = spec_path
        self.spec = None
        self.errors = []
        self.warnings = []
        self._load()
    
    def _load(self) -> None:
        """Load OpenAPI spec from YAML or JSON file."""
        with open(self.spec_path, 'r', encoding='utf-8') as f:
            if self.spec_path.endswith('.json'):
                self.spec = json.load(f)
            else:
                self.spec = yaml.safe_load(f)
    
    def validate(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            bool: True if no errors, False otherwise.
        """
        self._check_required_fields()
        self._check_paths()
        self._check_operations()
        self._check_parameters()
        self._check_responses()
        self._check_schemas()
        return len(self.errors) == 0
    
    def _check_required_fields(self) -> None:
        """Verify presence of required OpenAPI fields."""
        required = ['openapi', 'info', 'paths']
        for field in required:
            if field not in self.spec:
                self.errors.append(f"Missing required field: '{field}'")
        
        if 'info' in self.spec:
            info_required = ['title', 'version']
            for field in info_required:
                if field not in self.spec['info']:
                    self.errors.append(f"Missing required field: 'info.{field}'")
    
    def _check_paths(self) -> None:
        """Validate path structure and format."""
        paths = self.spec.get('paths', {})
        if not paths:
            self.warnings.append("No paths defined in the API")
        
        for path, path_item in paths.items():
            if not path.startswith('/'):
                self.errors.append(f"Path must start with '/': {path}")
            
            if not isinstance(path_item, dict):
                self.errors.append(f"Path '{path}' must be an object")
                continue
            
            # Validate HTTP methods (skip 'parameters' special key)
            valid_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']
            for method, operation in path_item.items():
                if method == 'parameters':
                    continue
                if method.lower() not in valid_methods:
                    self.errors.append(f"Invalid HTTP method '{method}' at path '{path}'")
    
    def _check_operations(self) -> None:
        """Validate HTTP operation structure."""
        valid_methods = ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method == 'parameters':
                    continue
                if method.lower() not in valid_methods:
                    self.errors.append(f"Invalid HTTP method '{method}' at path '{path}'")
                
                if isinstance(operation, dict):
                    if 'responses' not in operation:
                        self.warnings.append(f"Operation {method.upper()} {path} has no responses")
    
    def _check_parameters(self) -> None:
        """Validate parameter structure (name, location)."""
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method == 'parameters':
                    continue
                if not isinstance(operation, dict):
                    continue
                
                parameters = operation.get('parameters', [])
                for param in parameters:
                    if 'name' not in param:
                        self.errors.append(f"Parameter missing 'name' in {method.upper()} {path}")
                    if 'in' not in param:
                        self.errors.append(f"Parameter missing 'in' in {method.upper()} {path}")
    
    def _check_responses(self) -> None:
        """Validate response status codes."""
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method == 'parameters':
                    continue
                if not isinstance(operation, dict):
                    continue
                
                responses = operation.get('responses', {})
                if not responses:
                    continue
                
                for status_code, response in responses.items():
                    if status_code != 'default':
                        try:
                            int(status_code)  # Validate status code is numeric
                        except (ValueError, TypeError):
                            self.warnings.append(f"Non-standard status code '{status_code}' at {method.upper()} {path}")
    
    def _check_schemas(self) -> None:
        """Validate schema structure."""
        components = self.spec.get('components', {})
        schemas = components.get('schemas', {})
        
        for schema_name, schema in schemas.items():
            if not isinstance(schema, dict):
                self.errors.append(f"Schema '{schema_name}' must be an object")
    
    def get_report(self) -> str:
        """Generate human-readable validation report."""
        lines = []
        lines.append("=" * 60)
        lines.append("OpenAPI Validation Report")
        lines.append("=" * 60)
        lines.append(f"File: {self.spec_path}")
        lines.append("")
        
        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")
        
        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")
        
        if not self.errors and not self.warnings:
            lines.append("No issues found. Specification is valid.")
        elif self.errors:
            lines.append(f"Validation failed with {len(self.errors)} error(s)")
        else:
            lines.append(f"Validation passed with {len(self.warnings)} warning(s)")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def get_json_report(self) -> str:
        """Generate JSON-formatted validation report."""
        return json.dumps({
            "valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "file": self.spec_path
        }, indent=2)