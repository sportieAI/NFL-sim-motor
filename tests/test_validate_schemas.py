#!/usr/bin/env python3
"""
Test script to validate all JSON schemas under the schemas/ directory.
Ensures schema integrity and validates sample data against schemas.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

try:
    import jsonschema
    from jsonschema import validate, Draft202012Validator
except ImportError:
    print("ERROR: jsonschema package is required. Install with: pip install jsonschema")
    sys.exit(1)

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from schemas.schema_manager import SchemaManager
except ImportError:
    print("WARNING: Could not import SchemaManager, running basic JSON schema validation only")
    SchemaManager = None


def find_schema_files(schemas_dir: Path) -> List[Path]:
    """Find all JSON schema files in the schemas directory."""
    schema_files = []
    # Only search for .json files in the schemas directory (not recursively to avoid duplicates)
    schema_files.extend(schemas_dir.glob('*.json'))
    return sorted(set(schema_files))  # Remove duplicates and sort


def validate_json_schema(schema_path: Path) -> tuple[bool, str]:
    """Validate a single JSON schema file."""
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        
        # Validate the schema itself
        Draft202012Validator.check_schema(schema)
        
        # Create validator instance to check syntax
        validator = Draft202012Validator(schema)
        
        return True, f"✓ Schema {schema_path.name} is valid"
        
    except json.JSONDecodeError as e:
        return False, f"✗ Invalid JSON in {schema_path.name}: {e}"
    except jsonschema.SchemaError as e:
        return False, f"✗ Invalid schema {schema_path.name}: {e}"
    except Exception as e:
        return False, f"✗ Error validating {schema_path.name}: {e}"


def test_schema_manager_integration() -> tuple[bool, str]:
    """Test integration with SchemaManager if available."""
    if SchemaManager is None:
        return True, "⚠ SchemaManager not available - skipping integration tests"
    
    try:
        manager = SchemaManager()
        schemas = manager.get_all_schemas()
        
        if not schemas:
            return False, "✗ SchemaManager returned no schemas"
        
        # Test validation with sample data for each schema
        test_results = []
        for schema_name, versions in schemas.items():
            if not versions:
                continue
                
            # Get latest version
            latest_version = versions[-1]
            version_str = latest_version['version']
            
            # Get schema definition using the manager
            schema_def = manager.get_schema(schema_name, version_str)
            if not schema_def:
                test_results.append(f"✗ {schema_name} v{version_str}: Could not retrieve schema")
                continue
            
            # Create minimal test data based on schema
            test_data = create_test_data_for_schema(schema_def)
            
            # Validate test data
            is_valid, error = manager.validate(test_data, schema_name, version_str)
            if is_valid:
                test_results.append(f"✓ {schema_name} v{version_str}")
            else:
                test_results.append(f"✗ {schema_name} v{version_str}: {error}")
        
        return True, "Schema Manager Integration:\n  " + "\n  ".join(test_results)
        
    except Exception as e:
        return False, f"✗ SchemaManager integration test failed: {e}"


def create_test_data_for_schema(schema: Dict[str, Any]) -> Dict[str, Any]:
    """Create minimal test data that should validate against a schema."""
    test_data = {}
    
    if "properties" in schema:
        required_fields = schema.get("required", [])
        
        for field_name in required_fields:
            field_schema = schema["properties"].get(field_name, {})
            field_type = field_schema.get("type", "string")
            
            # Handle enum fields first
            if "enum" in field_schema:
                test_data[field_name] = field_schema["enum"][0]
            # Create appropriate test values based on type
            elif field_type == "string":
                test_data[field_name] = "test_value"
            elif field_type == "integer":
                test_data[field_name] = 1
            elif field_type == "number":
                test_data[field_name] = 1.0
            elif field_type == "boolean":
                test_data[field_name] = True
            elif field_type == "array":
                test_data[field_name] = []
            elif field_type == "object":
                test_data[field_name] = {}
    
    return test_data


def main():
    """Main test function."""
    print("🏈 NFL Simulation Engine - Schema Validation Tests")
    print("=" * 60)
    
    # Find schemas directory
    schemas_dir = PROJECT_ROOT / "schemas"
    if not schemas_dir.exists():
        print(f"ERROR: Schemas directory not found at {schemas_dir}")
        return 1
    
    # Find all schema files
    schema_files = find_schema_files(schemas_dir)
    if not schema_files:
        print(f"WARNING: No JSON schema files found in {schemas_dir}")
        return 0
    
    print(f"Found {len(schema_files)} schema files:")
    for schema_file in schema_files:
        print(f"  - {schema_file.relative_to(PROJECT_ROOT)}")
    
    print("\nValidating JSON schemas...")
    print("-" * 30)
    
    # Validate each schema file
    total_tests = 0
    passed_tests = 0
    
    for schema_file in schema_files:
        total_tests += 1
        is_valid, message = validate_json_schema(schema_file)
        print(message)
        if is_valid:
            passed_tests += 1
    
    # Test SchemaManager integration
    print("\nTesting SchemaManager integration...")
    print("-" * 40)
    total_tests += 1
    is_valid, message = test_schema_manager_integration()
    print(message)
    if is_valid:
        passed_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Schema Validation Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("✅ All schema validation tests PASSED!")
        return 0
    else:
        print("❌ Some schema validation tests FAILED!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)