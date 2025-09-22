#!/usr/bin/env python3
"""Convert OpenAPI JSON to YAML format and normalize simple anyOf unions.

This script reads api/openapi.json, rewrites common anyOf patterns like
  anyOf: [{type: string}, {type: null}]
into OpenAPI 3.1 JSON Schema unions using a type array:
  type: [string, "null"]

It also collapses simple multi-type unions like string|integer into
  type: [string, integer]

Finally it writes a clean YAML representation to docs/openapi.yaml.
"""

import json
from copy import deepcopy


def _is_null_schema(s):
    return isinstance(s, dict) and set(s.keys()) == {"type"} and s.get("type") == "null"


def _all_items_are_simple_types(schemas):
    # True if every item is a dict with only {"type": <primitive>} where primitive is a json schema type string
    if not isinstance(schemas, list) or not schemas:
        return False
    allowed_types = {"string", "integer", "number", "boolean", "object", "array", "null"}
    for s in schemas:
        if not isinstance(s, dict):
            return False
        # allow only 'type' key
        if set(s.keys()) != {"type"}:
            return False
        if s.get("type") not in allowed_types:
            return False
    return True


def normalize_anyof(node):
    """Recursively normalize simple anyOf constructs into type arrays.

    Rules:
    - anyOf of two items where one is exactly {type: null} and the other is a single-type schema
      becomes: type: [<type>, "null"], hoisting simple constraints (e.g., format, items, additionalProperties).
    - anyOf of N simple {type: X} items becomes: type: [X, ...].
    Other anyOf constructs are left as-is.
    """
    if isinstance(node, dict):
        node = {k: normalize_anyof(v) for k, v in node.items()}

        if "anyOf" in node and isinstance(node["anyOf"], list) and node["anyOf"]:
            alts = node["anyOf"]

            # Case 1: simple multi-type union (no extra constraints on branches)
            if _all_items_are_simple_types(alts):
                node.pop("anyOf", None)
                types = [s["type"] for s in alts]
                node["type"] = types
                return node

            # Case 2: null-able union with one non-null alt
            if len(alts) == 2 and any(_is_null_schema(a) for a in alts):
                non_null = next((a for a in alts if not _is_null_schema(a)), None)
                if isinstance(non_null, dict) and "type" in non_null:
                    node.pop("anyOf", None)
                    # Hoist constraints from the non-null branch
                    for k, v in non_null.items():
                        if k == "type":
                            continue
                        # Only set if not present at root to preserve explicit root keys
                        if k not in node:
                            node[k] = v
                    t = non_null.get("type")
                    # Merge with existing type if it's already an array or a string
                    existing_type = node.get("type")
                    if isinstance(existing_type, list):
                        types = list({*existing_type, t, "null"})
                    elif isinstance(existing_type, str):
                        types = [existing_type, t, "null"]
                    else:
                        types = [t, "null"]
                    node["type"] = types
                    return node

        return node

    if isinstance(node, list):
        return [normalize_anyof(v) for v in node]

    return node


def postprocess_openapi(doc: dict) -> dict:
    """Apply additional spec hygiene transformations for docs/Redocly:
    - Ensure root servers list exists if missing.
    - Replace empty schema objects (schema: {}) with permissive object schemas.
    """
    # 1) Servers
    if isinstance(doc, dict) and "servers" not in doc:
        doc["servers"] = [
            {"url": "http://localhost:8080", "description": "Local development server"},
            {"url": "https://api.faxbot.net", "description": "Production server"},
        ]

    # 2) Replace empty schemas
    def _walk(node):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if k == "schema" and isinstance(v, dict) and len(v) == 0:
                    node[k] = {"type": "object"}
                else:
                    _walk(v)
        elif isinstance(node, list):
            for i in range(len(node)):
                _walk(node[i])

    _walk(doc)

    # 3) Ensure operation descriptions and parameter descriptions exist (basic defaults)
    paths = doc.get("paths")
    if isinstance(paths, dict):
        for _path, methods in paths.items():
            if not isinstance(methods, dict):
                continue
            for method, op in methods.items():
                if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options", "trace"}:
                    continue
                if isinstance(op, dict):
                    # Ensure description exists
                    if "description" not in op and "summary" in op:
                        op["description"] = op.get("summary")

                    # Parameter descriptions
                    if isinstance(op.get("parameters"), list):
                        for p in op["parameters"]:
                            if isinstance(p, dict) and "description" not in p:
                                pname = p.get("name", "parameter")
                                pin = p.get("in", "")
                                if pname.lower() == "x-api-key" and pin == "header":
                                    p["description"] = "API key for authentication"
                                elif pin == "path":
                                    p["description"] = f"Path parameter: {pname}"
                                elif pin == "query":
                                    p["description"] = f"Query parameter: {pname}"
                                elif pin == "header":
                                    p["description"] = f"Header parameter: {pname}"
                                else:
                                    p["description"] = pname

    return doc


def json_to_yaml(obj, indent=0):
    """Simple JSON to YAML converter"""
    spaces = "  " * indent
    
    if isinstance(obj, dict):
        if not obj:
            return "{}"
        result = []
        for key, value in obj.items():
            # Escape special YAML characters in keys
            safe_key = str(key)
            if any(c in safe_key for c in [' ', ':', '"', "'", '\n', '-']) or safe_key.isdigit():
                safe_key = f'"{safe_key}"'
            
            yaml_value = json_to_yaml(value, indent + 1)
            if isinstance(value, (dict, list)) and value:
                result.append(f"{spaces}{safe_key}:")
                # Indent nested structures line by line for consistent formatting
                for line in yaml_value.split('\n'):
                    if line.strip():
                        result.append(f"  {line}")
            else:
                result.append(f"{spaces}{safe_key}: {yaml_value}")
        return '\n'.join(result)
    
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        result = []
        for item in obj:
            yaml_item = json_to_yaml(item, indent + 1)
            if isinstance(item, (dict, list)) and item:
                result.append(f"{spaces}-")
                for line in yaml_item.split('\n'):
                    if line.strip():
                        result.append(f"  {line}")
            else:
                result.append(f"{spaces}- {yaml_item}")
        return '\n'.join(result)
    
    elif isinstance(obj, str):
        # Handle multiline strings and special characters
        if '\n' in obj or '"' in obj or "'" in obj or obj.startswith(' ') or obj.endswith(' '):
            # Use literal block scalar for multiline
            if '\n' in obj:
                lines = obj.split('\n')
                result = ["|"]
                for line in lines:
                    result.append(f"{spaces}  {line}")
                return '\n'.join(result)
            else:
                # Quote strings with special characters
                escaped = obj.replace('"', '\\"')
                return f'"{escaped}"'
        # Quote YAML-reserved scalars to avoid misinterpretation
        if obj in ["null", "true", "false"] or obj.isdigit():
            return f'"{obj}"'
        return obj
    
    elif isinstance(obj, bool):
        return "true" if obj else "false"
    
    elif obj is None:
        return "null"
    
    else:
        return str(obj)

def main():
    # Read OpenAPI JSON (prefer freshly pulled root openapi.json; fallback to api/openapi.json)
    source_paths = [
        'openapi.json',           # user-provided fresh export (e.g., via curl | jq)
        'api/openapi.json',       # generated locally in repo
    ]
    for p in source_paths:
        try:
            with open(p, 'r') as f:
                openapi_data = json.load(f)
                source_used = p
                break
        except FileNotFoundError:
            continue
    else:
        raise FileNotFoundError("No OpenAPI JSON found. Provide openapi.json or api/openapi.json")

    # Normalize anyOf usage
    normalized = normalize_anyof(deepcopy(openapi_data))

    # Additional hygiene
    normalized = postprocess_openapi(normalized)

    # Convert to YAML
    yaml_content = json_to_yaml(normalized)

    # Write YAML file
    with open('docs/openapi.yaml', 'w') as f:
        f.write(yaml_content)

    print("✅ Converted + normalized OpenAPI at docs/openapi.yaml")
    print(f"📄 Source: {source_used}")
    print(f"📊 File size: {len(yaml_content):,} characters")

if __name__ == "__main__":
    main()
