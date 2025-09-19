"""
Test script to automatically validate all JSON Schema files in the schemas/ directory.
This ensures all schemas are always compliant with JSON Schema Draft 2020-12 specification.

Note: This test validates the schema files themselves for compliance, complementing
the existing schema_manager.py which validates schemas during registration.
This ensures that any schema files manually added or modified are properly validated in CI.
"""
import os
import json
from jsonschema import Draft202012Validator

SCHEMA_DIR = "schemas"

def test_all_jsonschemas():
    """
    Test that validates all JSON Schema files in the schemas/ directory.
    
    This test loops through all .json files in schemas/ and validates that
    each schema is compliant with JSON Schema Draft 2020-12 specification
    using Draft202012Validator.check_schema().
    """
    # Get absolute path to schemas directory
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_dir_path = os.path.join(current_dir, SCHEMA_DIR)
    
    # Ensure schemas directory exists
    assert os.path.exists(schema_dir_path), f"Schemas directory not found: {schema_dir_path}"
    
    # Get all JSON files in schemas directory
    json_files = [f for f in os.listdir(schema_dir_path) if f.endswith(".json")]
    
    # Ensure we have at least one schema file to test
    assert len(json_files) > 0, f"No JSON schema files found in {schema_dir_path}"
    
    # Track validation results for better reporting
    validated_count = 0
    
    # Test each schema file
    for file in json_files:
        file_path = os.path.join(schema_dir_path, file)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            raise AssertionError(f"Failed to read or parse JSON file {file}: {str(e)}")
        
        # Extract the actual schema from the metadata structure
        # Schema files contain metadata with the actual schema in a "schema" field
        if "schema" not in schema_data:
            raise AssertionError(f"Schema file {file} missing 'schema' field")
        
        schema = schema_data["schema"]
        
        # Validate that the schema itself is valid according to JSON Schema Draft 2020-12
        # This will raise an exception if the schema is invalid
        try:
            Draft202012Validator.check_schema(schema)
            validated_count += 1
            print(f"✅ Schema validation passed for {file}")
        except Exception as e:
            raise AssertionError(f"Schema validation failed for {file}: {str(e)}")
    
    # Final assertion to ensure we actually validated schemas
    assert validated_count > 0, "No schemas were successfully validated"
    print(f"✅ All {validated_count} JSON schemas validated successfully")

if __name__ == "__main__":
    # Allow running the test directly
    test_all_jsonschemas()
    print("All schema validations passed!")