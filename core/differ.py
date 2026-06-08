"""
OpenAPI Specification Differ

Compares two OpenAPI specifications and detects changes in:
- Endpoints (paths)
- HTTP methods
- Parameters (added, removed, modified)
- Schemas (added, removed, property changes)
"""

import yaml
import json
from typing import Dict, Any, Set, List, Tuple


class OpenAPIDiffer:
    """
    Compare two OpenAPI specifications and detect changes.
    
    Attributes:
        old_spec_path (str): Path to the old specification.
        new_spec_path (str): Path to the new specification.
        old_spec (dict): Loaded old specification.
        new_spec (dict): Loaded new specification.
    """
    
    def __init__(self, old_spec_path: str, new_spec_path: str):
        """Initialize differ with two specification paths."""
        self.old_spec_path = old_spec_path
        self.new_spec_path = new_spec_path
        self.old_spec = self._load_spec(old_spec_path)
        self.new_spec = self._load_spec(new_spec_path)
    
    def _load_spec(self, path: str) -> Dict[str, Any]:
        """Load OpenAPI spec from YAML or JSON file."""
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f)
    
    def _get_all_paths(self, spec: Dict[str, Any]) -> Set[str]:
        """Get all endpoint paths from a spec."""
        return set(spec.get('paths', {}).keys())
    
    def _get_all_methods(self, spec: Dict[str, Any], path: str) -> Set[str]:
        """Get all HTTP methods for a given path."""
        path_obj = spec.get('paths', {}).get(path, {})
        methods = set()
        for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
            if method in path_obj:
                methods.add(method)
        return methods
    
    def _get_parameters(self, spec: Dict[str, Any], path: str, method: str) -> Dict[str, Any]:
        """
        Get all parameters for a specific endpoint.
        
        Returns:
            dict: Dictionary keyed by "{name}_{in}" for easy comparison.
        """
        path_obj = spec.get('paths', {}).get(path, {})
        method_obj = path_obj.get(method, {})
        parameters = method_obj.get('parameters', [])
        param_dict = {}
        for param in parameters:
            name = param.get('name', '')
            param_in = param.get('in', '')
            key = f"{name}_{param_in}"
            param_dict[key] = param
        return param_dict
    
    def _get_schemas(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Get all schemas from components."""
        components = spec.get('components', {})
        return components.get('schemas', {})
    
    def _get_schema_properties(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Get properties of a schema."""
        return schema.get('properties', {})
    
    def detect_added_paths(self) -> List[str]:
        """Find paths that exist in new spec but not in old spec."""
        old_paths = self._get_all_paths(self.old_spec)
        new_paths = self._get_all_paths(self.new_spec)
        return list(new_paths - old_paths)
    
    def detect_removed_paths(self) -> List[str]:
        """Find paths that exist in old spec but not in new spec."""
        old_paths = self._get_all_paths(self.old_spec)
        new_paths = self._get_all_paths(self.new_spec)
        return list(old_paths - new_paths)
    
    def detect_added_methods(self) -> List[Tuple[str, str]]:
        """Find HTTP methods added to existing paths."""
        added = []
        old_paths = self._get_all_paths(self.old_spec)
        new_paths = self._get_all_paths(self.new_spec)
        common_paths = old_paths & new_paths
        
        for path in common_paths:
            old_methods = self._get_all_methods(self.old_spec, path)
            new_methods = self._get_all_methods(self.new_spec, path)
            added_methods = new_methods - old_methods
            for method in added_methods:
                added.append((path, method))
        
        return added
    
    def detect_removed_methods(self) -> List[Tuple[str, str]]:
        """Find HTTP methods removed from existing paths."""
        removed = []
        old_paths = self._get_all_paths(self.old_spec)
        new_paths = self._get_all_paths(self.new_spec)
        common_paths = old_paths & new_paths
        
        for path in common_paths:
            old_methods = self._get_all_methods(self.old_spec, path)
            new_methods = self._get_all_methods(self.new_spec, path)
            removed_methods = old_methods - new_methods
            for method in removed_methods:
                removed.append((path, method))
        
        return removed
    
    def detect_parameter_changes(self) -> List[Tuple[str, str, str, str]]:
        """
        Detect parameter changes on existing endpoints.
        
        Returns:
            list of (path, method, change_type, param_name)
            change_type: 'added', 'removed', 'required_changed', 'description_changed'
        """
        changes = []
        old_paths = self._get_all_paths(self.old_spec)
        new_paths = self._get_all_paths(self.new_spec)
        common_paths = old_paths & new_paths
        
        for path in common_paths:
            old_methods = self._get_all_methods(self.old_spec, path)
            new_methods = self._get_all_methods(self.new_spec, path)
            common_methods = old_methods & new_methods
            
            for method in common_methods:
                old_params = self._get_parameters(self.old_spec, path, method)
                new_params = self._get_parameters(self.new_spec, path, method)
                
                # Added parameters
                for param_key in new_params:
                    if param_key not in old_params:
                        param_name = new_params[param_key].get('name', param_key)
                        changes.append((path, method, 'added', param_name))
                
                # Removed parameters
                for param_key in old_params:
                    if param_key not in new_params:
                        param_name = old_params[param_key].get('name', param_key)
                        changes.append((path, method, 'removed', param_name))
                
                # Modified parameters
                for param_key in old_params:
                    if param_key in new_params:
                        old_param = old_params[param_key]
                        new_param = new_params[param_key]
                        
                        # Required flag changed
                        old_required = old_param.get('required', False)
                        new_required = new_param.get('required', False)
                        if old_required != new_required:
                            param_name = old_param.get('name', param_key)
                            changes.append((path, method, 'required_changed', param_name))
                        
                        # Description changed
                        old_desc = old_param.get('description', '')
                        new_desc = new_param.get('description', '')
                        if old_desc != new_desc:
                            param_name = old_param.get('name', param_key)
                            changes.append((path, method, 'description_changed', param_name))
        
        return changes
    
    def detect_schema_changes(self) -> Dict[str, List]:
        """
        Detect changes in schemas.
        
        Returns:
            dict with keys: 'added', 'removed', 'property_added', 
            'property_removed', 'property_modified'
        """
        changes = {
            'added': [],
            'removed': [],
            'property_added': [],
            'property_removed': [],
            'property_modified': []
        }
        
        old_schemas = self._get_schemas(self.old_spec)
        new_schemas = self._get_schemas(self.new_spec)
        
        old_names = set(old_schemas.keys())
        new_names = set(new_schemas.keys())
        
        # Added/removed schemas
        changes['added'] = list(new_names - old_names)
        changes['removed'] = list(old_names - new_names)
        
        # Property changes within common schemas
        for name in old_names & new_names:
            old_props = self._get_schema_properties(old_schemas[name])
            new_props = self._get_schema_properties(new_schemas[name])
            
            old_prop_names = set(old_props.keys())
            new_prop_names = set(new_props.keys())
            
            # Added/removed properties
            for prop in new_prop_names - old_prop_names:
                changes['property_added'].append(f"{name}.{prop}")
            
            for prop in old_prop_names - new_prop_names:
                changes['property_removed'].append(f"{name}.{prop}")
            
            # Modified properties (type or description)
            for prop in old_prop_names & new_prop_names:
                old_type = old_props[prop].get('type', 'unknown')
                new_type = new_props[prop].get('type', 'unknown')
                if old_type != new_type:
                    changes['property_modified'].append(
                        f"{name}.{prop}: type changed from '{old_type}' to '{new_type}'"
                    )
                else:
                    old_desc = old_props[prop].get('description', '')
                    new_desc = new_props[prop].get('description', '')
                    if old_desc != new_desc:
                        changes['property_modified'].append(f"{name}.{prop}: description changed")
        
        return changes
    
    def generate_report(self, format: str = 'text') -> str:
        """
        Generate diff report in text or markdown format.
        
        Args:
            format: 'text' for human-readable, 'markdown' for PR comments.
        
        Returns:
            str: Formatted report.
        """
        if format == 'markdown':
            return self._generate_markdown_report()
        return self._generate_text_report()
    
    def _generate_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = []
        lines.append("=" * 60)
        lines.append("API Changes Summary")
        lines.append("=" * 60)
        lines.append("")
        
        # Endpoint changes
        added_paths = self.detect_added_paths()
        if added_paths:
            lines.append(f"Added endpoints ({len(added_paths)}):")
            for path in added_paths:
                lines.append(f"  - {path}")
            lines.append("")
        
        removed_paths = self.detect_removed_paths()
        if removed_paths:
            lines.append(f"Removed endpoints ({len(removed_paths)}):")
            for path in removed_paths:
                lines.append(f"  - {path}")
            lines.append("")
        
        # Method changes
        added_methods = self.detect_added_methods()
        if added_methods:
            lines.append(f"Added HTTP methods ({len(added_methods)}):")
            for path, method in added_methods:
                lines.append(f"  - {method.upper()} {path}")
            lines.append("")
        
        removed_methods = self.detect_removed_methods()
        if removed_methods:
            lines.append(f"Removed HTTP methods ({len(removed_methods)}):")
            for path, method in removed_methods:
                lines.append(f"  - {method.upper()} {path}")
            lines.append("")
        
        # Parameter changes
        param_changes = self.detect_parameter_changes()
        if param_changes:
            added_params = [c for c in param_changes if c[2] == 'added']
            removed_params = [c for c in param_changes if c[2] == 'removed']
            modified_params = [c for c in param_changes if c[2] in ['required_changed', 'description_changed']]
            
            if added_params:
                lines.append(f"Added parameters ({len(added_params)}):")
                for path, method, change, param_name in added_params:
                    lines.append(f"  - {method.upper()} {path}: added parameter '{param_name}'")
                lines.append("")
            
            if removed_params:
                lines.append(f"Removed parameters ({len(removed_params)}):")
                for path, method, change, param_name in removed_params:
                    lines.append(f"  - {method.upper()} {path}: removed parameter '{param_name}'")
                lines.append("")
            
            if modified_params:
                lines.append(f"Modified parameters ({len(modified_params)}):")
                for path, method, change, param_name in modified_params:
                    change_type = "required flag changed" if change == 'required_changed' else "description changed"
                    lines.append(f"  - {method.upper()} {path}: parameter '{param_name}' — {change_type}")
                lines.append("")
        
        # Schema changes
        schema_changes = self.detect_schema_changes()
        
        if schema_changes['added']:
            lines.append(f"Added schemas ({len(schema_changes['added'])}):")
            for schema in schema_changes['added']:
                lines.append(f"  - {schema}")
            lines.append("")
        
        if schema_changes['removed']:
            lines.append(f"Removed schemas ({len(schema_changes['removed'])}):")
            for schema in schema_changes['removed']:
                lines.append(f"  - {schema}")
            lines.append("")
        
        if schema_changes['property_added']:
            lines.append(f"Added properties ({len(schema_changes['property_added'])}):")
            for prop in schema_changes['property_added']:
                lines.append(f"  - {prop}")
            lines.append("")
        
        if schema_changes['property_removed']:
            lines.append(f"Removed properties ({len(schema_changes['property_removed'])}):")
            for prop in schema_changes['property_removed']:
                lines.append(f"  - {prop}")
            lines.append("")
        
        if schema_changes['property_modified']:
            lines.append(f"Modified properties ({len(schema_changes['property_modified'])}):")
            for prop in schema_changes['property_modified']:
                lines.append(f"  - {prop}")
            lines.append("")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def _generate_markdown_report(self) -> str:
        """Generate Markdown report suitable for PR comments."""
        lines = []
        lines.append("## API Changes Summary\n")
        
        added_paths = self.detect_added_paths()
        if added_paths:
            lines.append(f"### Added Endpoints ({len(added_paths)})")
            for path in added_paths:
                lines.append(f"- `{path}`")
            lines.append("")
        
        removed_paths = self.detect_removed_paths()
        if removed_paths:
            lines.append(f"### Removed Endpoints ({len(removed_paths)})")
            for path in removed_paths:
                lines.append(f"- `{path}`")
            lines.append("")
        
        added_methods = self.detect_added_methods()
        if added_methods:
            lines.append(f"### Added HTTP Methods ({len(added_methods)})")
            for path, method in added_methods:
                lines.append(f"- `{method.upper()} {path}`")
            lines.append("")
        
        removed_methods = self.detect_removed_methods()
        if removed_methods:
            lines.append(f"### Removed HTTP Methods ({len(removed_methods)})")
            for path, method in removed_methods:
                lines.append(f"- `{method.upper()} {path}`")
            lines.append("")
        
        param_changes = self.detect_parameter_changes()
        if param_changes:
            added_params = [c for c in param_changes if c[2] == 'added']
            removed_params = [c for c in param_changes if c[2] == 'removed']
            modified_params = [c for c in param_changes if c[2] in ['required_changed', 'description_changed']]
            
            if added_params:
                lines.append(f"### Added Parameters ({len(added_params)})")
                for path, method, change, param_name in added_params:
                    lines.append(f"- `{method.upper()} {path}`: added `{param_name}`")
                lines.append("")
            
            if removed_params:
                lines.append(f"### Removed Parameters ({len(removed_params)})")
                for path, method, change, param_name in removed_params:
                    lines.append(f"- `{method.upper()} {path}`: removed `{param_name}`")
                lines.append("")
            
            if modified_params:
                lines.append(f"### Modified Parameters ({len(modified_params)})")
                for path, method, change, param_name in modified_params:
                    change_type = "required flag changed" if change == 'required_changed' else "description changed"
                    lines.append(f"- `{method.upper()} {path}`: `{param_name}` — {change_type}")
                lines.append("")
        
        schema_changes = self.detect_schema_changes()
        
        if schema_changes['added']:
            lines.append(f"### Added Schemas ({len(schema_changes['added'])})")
            for schema in schema_changes['added']:
                lines.append(f"- `{schema}`")
            lines.append("")
        
        if schema_changes['removed']:
            lines.append(f"### Removed Schemas ({len(schema_changes['removed'])})")
            for schema in schema_changes['removed']:
                lines.append(f"- `{schema}`")
            lines.append("")
        
        if schema_changes['property_added']:
            lines.append(f"### Added Properties ({len(schema_changes['property_added'])})")
            for prop in schema_changes['property_added']:
                lines.append(f"- `{prop}`")
            lines.append("")
        
        if schema_changes['property_removed']:
            lines.append(f"### Removed Properties ({len(schema_changes['property_removed'])})")
            for prop in schema_changes['property_removed']:
                lines.append(f"- `{prop}`")
            lines.append("")
        
        if schema_changes['property_modified']:
            lines.append(f"### Modified Properties ({len(schema_changes['property_modified'])})")
            for prop in schema_changes['property_modified']:
                lines.append(f"- `{prop}`")
            lines.append("")
        
        if not any([added_paths, removed_paths, added_methods, removed_methods, 
                    param_changes, schema_changes['added'], schema_changes['removed'],
                    schema_changes['property_added'], schema_changes['property_removed'],
                    schema_changes['property_modified']]):
            lines.append("**No changes detected**")
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> str:
        """Generate structured JSON report for machine consumption."""
        report = {
            "added_endpoints": self.detect_added_paths(),
            "removed_endpoints": self.detect_removed_paths(),
            "added_methods": [{"path": p, "method": m} for p, m in self.detect_added_methods()],
            "removed_methods": [{"path": p, "method": m} for p, m in self.detect_removed_methods()],
            "parameters": {"added": [], "removed": [], "modified": []},
            "schemas": {
                "added": [],
                "removed": [],
                "property_added": [],
                "property_removed": [],
                "property_modified": []
            }
        }
        
        # Parameter changes
        param_changes = self.detect_parameter_changes()
        for path, method, change_type, param_name in param_changes:
            entry = {"path": path, "method": method, "name": param_name}
            if change_type == 'added':
                report["parameters"]["added"].append(entry)
            elif change_type == 'removed':
                report["parameters"]["removed"].append(entry)
            else:
                entry["change"] = change_type
                report["parameters"]["modified"].append(entry)
        
        # Schema changes
        schema_changes = self.detect_schema_changes()
        report["schemas"]["added"] = schema_changes['added']
        report["schemas"]["removed"] = schema_changes['removed']
        report["schemas"]["property_added"] = schema_changes['property_added']
        report["schemas"]["property_removed"] = schema_changes['property_removed']
        report["schemas"]["property_modified"] = schema_changes['property_modified']
        
        # Summary counts
        report["summary"] = {
            "total_added_endpoints": len(report["added_endpoints"]),
            "total_removed_endpoints": len(report["removed_endpoints"]),
            "total_added_methods": len(report["added_methods"]),
            "total_removed_methods": len(report["removed_methods"]),
            "total_added_parameters": len(report["parameters"]["added"]),
            "total_removed_parameters": len(report["parameters"]["removed"]),
            "total_modified_parameters": len(report["parameters"]["modified"]),
            "total_added_schemas": len(report["schemas"]["added"]),
            "total_removed_schemas": len(report["schemas"]["removed"]),
            "total_added_properties": len(report["schemas"]["property_added"]),
            "total_removed_properties": len(report["schemas"]["property_removed"]),
            "total_modified_properties": len(report["schemas"]["property_modified"])
        }
        
        return json.dumps(report, indent=2)