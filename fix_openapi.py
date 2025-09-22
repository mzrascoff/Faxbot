#!/usr/bin/env python3
"""Fix OpenAPI YAML formatting issues"""

import json
import re

def fix_yaml_structure(data, indent=0):
    """Convert JSON to properly formatted YAML"""
    spaces = "  " * indent
    
    if isinstance(data, dict):
        if not data:
            return "{}"
        
        result = []
        for key, value in data.items():
            # Handle special keys that need quoting
            safe_key = str(key)
            if any(c in safe_key for c in [' ', ':', '"', "'", '\n', '-']) or safe_key.isdigit():
                safe_key = f'"{safe_key}"'
            
            if isinstance(value, (dict, list)) and value:
                result.append(f"{spaces}{safe_key}:")
                yaml_value = fix_yaml_structure(value, indent + 1)
                for line in yaml_value.split('\n'):
                    if line.strip():
                        result.append(f"  {line}")
            else:
                yaml_value = fix_yaml_structure(value, indent)
                result.append(f"{spaces}{safe_key}: {yaml_value}")
        
        return '\n'.join(result)
    
    elif isinstance(data, list):
        if not data:
            return "[]"
        
        result = []
        for item in data:
            if isinstance(item, (dict, list)) and item:
                result.append(f"{spaces}-")
                yaml_item = fix_yaml_structure(item, indent + 1)
                for line in yaml_item.split('\n'):
                    if line.strip():
                        result.append(f"  {line}")
            else:
                yaml_item = fix_yaml_structure(item, indent)
                result.append(f"{spaces}- {yaml_item}")
        
        return '\n'.join(result)
    
    elif isinstance(data, str):
        # Handle special string values
        if data in ['null', 'true', 'false'] or data.isdigit():
            return f'"{data}"'
        
        # Handle multiline strings
        if '\n' in data:
            lines = data.split('\n')
            result = ["|"]
            for line in lines:
                result.append(f"{spaces}  {line}")
            return '\n'.join(result)
        
        # Quote strings that need it
        if any(c in data for c in [':', '"', "'", '\n', '#']) or data.startswith(' ') or data.endswith(' '):
            escaped = data.replace('"', '\\"')
            return f'"{escaped}"'
        
        return data
    
    elif isinstance(data, bool):
        return "true" if data else "false"
    
    elif data is None:
        return "null"
    
    else:
        return str(data)

def main():
    # Read OpenAPI JSON
    with open('api/openapi.json', 'r') as f:
        openapi_data = json.load(f)
    
    # Convert to fixed YAML
    yaml_content = fix_yaml_structure(openapi_data)
    
    # Write fixed YAML
    with open('docs/openapi_fixed.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("✅ Created fixed OpenAPI YAML")
    print(f"📊 Size: {len(yaml_content):,} characters")

if __name__ == "__main__":
    main()
