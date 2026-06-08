"""
OpenAPI Specification Parser

Parses OpenAPI (Swagger) specification files in YAML or JSON format.
Provides methods to access API info, paths, and components/schemas.
"""

import yaml
import json
from typing import Dict, Any
import click


class OpenAPIParser:
    """
    Parse and provide access to OpenAPI specification content.
    
    Attributes:
        spec_path (str): Path to the OpenAPI spec file.
        spec (dict): Loaded OpenAPI specification.
    """
    
    def __init__(self, spec_path: str):
        """
        Initialize the parser and load the specification.
        
        Args:
            spec_path: Path to OpenAPI spec file (YAML or JSON).
        """
        self.spec_path = spec_path
        self.spec = None
        self._load()
    
    def _load(self) -> None:
        """Load OpenAPI spec from YAML or JSON file."""
        try:
            with open(self.spec_path, 'r', encoding='utf-8') as f:
                if self.spec_path.endswith('.json'):
                    self.spec = json.load(f)
                else:
                    self.spec = yaml.safe_load(f)
            
            info = self.spec.get('info', {})
            click.echo(f"[OK] Loaded spec: {info.get('title', 'Untitled API')} v{info.get('version', 'N/A')}")
        except Exception as e:
            click.echo(f"[ERROR] Failed to load spec: {e}", err=True)
            raise
    
    def get_info(self) -> Dict[str, Any]:
        """Return API info section (title, version, description)."""
        return self.spec.get('info', {})
    
    def get_paths(self) -> Dict[str, Any]:
        """Return all API paths and their operations."""
        return self.spec.get('paths', {})
    
    def get_components(self) -> Dict[str, Any]:
        """Return components/schemas section."""
        return self.spec.get('components', {})