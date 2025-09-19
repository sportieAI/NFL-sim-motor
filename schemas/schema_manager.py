"""
JSON Schema management with versioning and backward compatibility.
Provides comprehensive schema validation and migration support.
"""

import json
import time
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

try:
    import jsonschema

    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from ontology.version_manager import SemanticVersion


@dataclass
class SchemaVersion:
    """Represents a versioned JSON schema."""

    schema_name: str
    version: SemanticVersion
    schema: Dict[str, Any]
    created_at: float
    deprecated: bool = False
    deprecation_date: Optional[float] = None
    replacement_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "schema_name": self.schema_name,
            "version": str(self.version),
            "schema": self.schema,
            "created_at": self.created_at,
            "deprecated": self.deprecated,
            "deprecation_date": self.deprecation_date,
            "replacement_version": self.replacement_version,
        }


class SchemaManager:
    """Manages versioned JSON schemas with backward compatibility."""

    def __init__(self, storage_path: str = "schemas"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.schemas: Dict[str, Dict[str, SchemaVersion]] = (
            {}
        )  # schema_name -> version -> SchemaVersion
        self.current_versions: Dict[str, SemanticVersion] = {}
        self.logger = logging.getLogger(__name__)

        # Load existing schemas
        self._load_schemas()

        # Initialize default schemas if none exist
        if not self.schemas:
            self._initialize_default_schemas()

    def _load_schemas(self):
        """Load all schema versions from storage."""
        for schema_file in self.storage_path.glob("*.json"):
            try:
                with open(schema_file, "r") as f:
                    data = json.load(f)

                schema_version = SchemaVersion(
                    schema_name=data["schema_name"],
                    version=SemanticVersion.from_string(data["version"]),
                    schema=data["schema"],
                    created_at=data["created_at"],
                    deprecated=data.get("deprecated", False),
                    deprecation_date=data.get("deprecation_date"),
                    replacement_version=data.get("replacement_version"),
                )

                # Store in nested structure
                if schema_version.schema_name not in self.schemas:
                    self.schemas[schema_version.schema_name] = {}

                self.schemas[schema_version.schema_name][
                    str(schema_version.version)
                ] = schema_version

                # Track current version for each schema
                if not schema_version.deprecated:
                    current = self.current_versions.get(schema_version.schema_name)
                    if not current or schema_version.version > current:
                        self.current_versions[schema_version.schema_name] = (
                            schema_version.version
                        )

            except Exception as e:
                self.logger.error(f"Failed to load schema from {schema_file}: {e}")

    def _initialize_default_schemas(self):
        """Initialize with default NFL simulation schemas."""
        # Game State Schema
        game_state_v1 = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "title": "NFL Game State",
            "description": "Current state of an NFL game simulation",
            "required": [
                "down",
                "distance",
                "field_position",
                "quarter",
                "time_remaining",
            ],
            "properties": {
                "down": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Current down (1-4)",
                },
                "distance": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 99,
                    "description": "Yards to go for first down",
                },
                "field_position": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Yards from own goal line",
                },
                "quarter": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 4,
                    "description": "Current quarter",
                },
                "time_remaining": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 3600,
                    "description": "Seconds remaining in game",
                },
                "score_differential": {
                    "type": "integer",
                    "description": "Point differential (positive = leading)",
                },
                "timeouts_remaining": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 3,
                    "description": "Timeouts remaining for possession team",
                },
                "possession_team": {
                    "type": "string",
                    "enum": ["HOME", "AWAY"],
                    "description": "Team currently possessing the ball",
                },
            },
        }

        self.register_schema("game_state", SemanticVersion(1, 0, 0), game_state_v1)

        # Play Result Schema
        play_result_v1 = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "title": "NFL Play Result",
            "description": "Result of an executed play",
            "required": ["play_id", "play_type", "yards_gained", "timestamp"],
            "properties": {
                "play_id": {
                    "type": "string",
                    "description": "Unique identifier for the play",
                },
                "play_type": {
                    "type": "string",
                    "enum": [
                        "run",
                        "pass_short",
                        "pass_medium",
                        "pass_deep",
                        "punt",
                        "field_goal",
                        "extra_point",
                    ],
                    "description": "Type of play executed",
                },
                "yards_gained": {
                    "type": "integer",
                    "minimum": -20,
                    "maximum": 100,
                    "description": "Yards gained on the play",
                },
                "timestamp": {
                    "type": "number",
                    "description": "Unix timestamp of play execution",
                },
                "turnover": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether play resulted in turnover",
                },
                "touchdown": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether play resulted in touchdown",
                },
                "first_down": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether play achieved first down",
                },
                "penalty": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether play had penalty",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags applied to the play",
                },
            },
        }

        self.register_schema("play_result", SemanticVersion(1, 0, 0), play_result_v1)

        # Error Report Schema
        error_report_v1 = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "title": "Error Report",
            "description": "Structured error report from simulation",
            "required": ["error_id", "error_type", "message", "timestamp", "severity"],
            "properties": {
                "error_id": {
                    "type": "string",
                    "description": "Unique identifier for the error",
                },
                "error_type": {"type": "string", "description": "Type/class of error"},
                "message": {
                    "type": "string",
                    "description": "Human-readable error message",
                },
                "timestamp": {
                    "type": "number",
                    "description": "Unix timestamp when error occurred",
                },
                "severity": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                    "description": "Severity level of the error",
                },
                "play_context": {
                    "type": "object",
                    "description": "Context information about the play when error occurred",
                },
                "stacktrace": {
                    "type": "string",
                    "description": "Full stacktrace if available",
                },
                "recoverable": {
                    "type": "boolean",
                    "default": True,
                    "description": "Whether the error is recoverable",
                },
            },
        }

        self.register_schema("error_report", SemanticVersion(1, 0, 0), error_report_v1)

    def register_schema(
        self, schema_name: str, version: SemanticVersion, schema: Dict[str, Any]
    ) -> bool:
        """Register a new schema version."""
        try:
            # Validate the schema itself
            if JSONSCHEMA_AVAILABLE:
                jsonschema.Draft202012Validator.check_schema(schema)

            schema_version = SchemaVersion(
                schema_name=schema_name,
                version=version,
                schema=schema,
                created_at=time.time(),
            )

            # Store schema
            if schema_name not in self.schemas:
                self.schemas[schema_name] = {}

            self.schemas[schema_name][str(version)] = schema_version

            # Update current version
            current = self.current_versions.get(schema_name)
            if not current or version > current:
                self.current_versions[schema_name] = version

            # Persist to disk
            self._save_schema(schema_version)

            self.logger.info(f"Registered schema {schema_name} v{version}")
            return True

        except Exception as e:
            self.logger.error(
                f"Failed to register schema {schema_name} v{version}: {e}"
            )
            return False

    def validate(
        self, data: Dict[str, Any], schema_name: str, version: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """Validate data against a schema."""
        if not JSONSCHEMA_AVAILABLE:
            self.logger.warning("jsonschema not available, skipping validation")
            return True, None

        if schema_name not in self.schemas:
            return False, f"Schema '{schema_name}' not found"

        # Use current version if not specified
        if version is None:
            if schema_name not in self.current_versions:
                return False, f"No current version found for schema '{schema_name}'"
            version = str(self.current_versions[schema_name])

        if version not in self.schemas[schema_name]:
            return False, f"Schema '{schema_name}' version '{version}' not found"

        schema = self.schemas[schema_name][version].schema

        try:
            jsonschema.validate(data, schema)
            return True, None
        except jsonschema.ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    def get_schema(
        self, schema_name: str, version: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a schema by name and version."""
        if schema_name not in self.schemas:
            return None

        if version is None:
            if schema_name not in self.current_versions:
                return None
            version = str(self.current_versions[schema_name])

        schema_version = self.schemas[schema_name].get(version)
        return schema_version.schema if schema_version else None

    def deprecate_schema_version(
        self, schema_name: str, version: str, replacement_version: Optional[str] = None
    ) -> bool:
        """Deprecate a specific schema version."""
        if schema_name not in self.schemas or version not in self.schemas[schema_name]:
            return False

        schema_version = self.schemas[schema_name][version]
        schema_version.deprecated = True
        schema_version.deprecation_date = time.time()
        schema_version.replacement_version = replacement_version

        # Save updated schema
        self._save_schema(schema_version)

        self.logger.info(f"Deprecated schema {schema_name} v{version}")
        return True

    def get_migration_instructions(
        self, schema_name: str, from_version: str, to_version: str
    ) -> List[Dict[str, Any]]:
        """Get migration instructions between schema versions."""
        if (
            schema_name not in self.schemas
            or from_version not in self.schemas[schema_name]
            or to_version not in self.schemas[schema_name]
        ):
            return []

        from_schema = self.schemas[schema_name][from_version].schema
        to_schema = self.schemas[schema_name][to_version].schema

        instructions = []

        # Compare required fields
        from_required = set(from_schema.get("required", []))
        to_required = set(to_schema.get("required", []))

        new_required = to_required - from_required
        removed_required = from_required - to_required

        for field in new_required:
            instructions.append(
                {
                    "action": "add_required_field",
                    "field": field,
                    "description": f"Field '{field}' is now required",
                }
            )

        for field in removed_required:
            instructions.append(
                {
                    "action": "remove_required_field",
                    "field": field,
                    "description": f"Field '{field}' is no longer required",
                }
            )

        # Compare properties
        from_props = from_schema.get("properties", {})
        to_props = to_schema.get("properties", {})

        new_props = set(to_props.keys()) - set(from_props.keys())
        removed_props = set(from_props.keys()) - set(to_props.keys())

        for prop in new_props:
            instructions.append(
                {
                    "action": "add_property",
                    "property": prop,
                    "description": f"New property '{prop}' added",
                }
            )

        for prop in removed_props:
            instructions.append(
                {
                    "action": "remove_property",
                    "property": prop,
                    "description": f"Property '{prop}' removed",
                }
            )

        return instructions

    def get_all_schemas(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all schemas with version information."""
        result = {}

        for schema_name, versions in self.schemas.items():
            result[schema_name] = []
            for version_str, schema_version in sorted(
                versions.items(), key=lambda x: x[1].version
            ):
                result[schema_name].append(
                    {
                        "version": version_str,
                        "created_at": schema_version.created_at,
                        "deprecated": schema_version.deprecated,
                        "deprecation_date": schema_version.deprecation_date,
                        "replacement_version": schema_version.replacement_version,
                        "is_current": version_str
                        == str(self.current_versions.get(schema_name)),
                    }
                )

        return result

    def _save_schema(self, schema_version: SchemaVersion):
        """Save schema version to disk."""
        try:
            filename = f"{schema_version.schema_name}_v{schema_version.version}.json"
            file_path = self.storage_path / filename

            with open(file_path, "w") as f:
                json.dump(schema_version.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(
                f"Failed to save schema {schema_version.schema_name} v{schema_version.version}: {e}"
            )


class SchemaTestRunner:
    """Runs comprehensive tests for all schemas."""

    def __init__(self, schema_manager: SchemaManager):
        self.schema_manager = schema_manager
        self.logger = logging.getLogger(__name__)

    def run_all_schema_tests(self) -> Dict[str, Any]:
        """Run tests for all schemas."""
        results = {
            "total_schemas": 0,
            "passed_schemas": 0,
            "failed_schemas": 0,
            "schema_results": {},
            "overall_success": True,
        }

        all_schemas = self.schema_manager.get_all_schemas()

        for schema_name in all_schemas:
            results["total_schemas"] += 1

            schema_result = self._test_schema(schema_name)
            results["schema_results"][schema_name] = schema_result

            if schema_result["success"]:
                results["passed_schemas"] += 1
            else:
                results["failed_schemas"] += 1
                results["overall_success"] = False

        return results

    def _test_schema(self, schema_name: str) -> Dict[str, Any]:
        """Test a specific schema with various test cases."""
        result = {"success": True, "test_cases": [], "error_count": 0}

        # Get current schema
        schema = self.schema_manager.get_schema(schema_name)
        if not schema:
            return {"success": False, "error": f"Schema {schema_name} not found"}

        # Generate test cases based on schema type
        test_cases = self._generate_test_cases(schema_name, schema)

        for test_case in test_cases:
            is_valid, error = self.schema_manager.validate(
                test_case["data"], schema_name
            )

            test_result = {
                "description": test_case["description"],
                "expected_valid": test_case["expected_valid"],
                "actual_valid": is_valid,
                "success": (is_valid == test_case["expected_valid"]),
                "error": error if not is_valid else None,
            }

            result["test_cases"].append(test_result)

            if not test_result["success"]:
                result["success"] = False
                result["error_count"] += 1

        return result

    def _generate_test_cases(
        self, schema_name: str, schema: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate test cases for a schema."""
        test_cases = []

        if schema_name == "game_state":
            # Valid cases
            test_cases.extend(
                [
                    {
                        "description": "Valid game state",
                        "data": {
                            "down": 1,
                            "distance": 10,
                            "field_position": 25,
                            "quarter": 1,
                            "time_remaining": 3600,
                            "score_differential": 0,
                            "possession_team": "HOME",
                        },
                        "expected_valid": True,
                    },
                    {
                        "description": "Minimal valid game state",
                        "data": {
                            "down": 3,
                            "distance": 7,
                            "field_position": 65,
                            "quarter": 4,
                            "time_remaining": 120,
                        },
                        "expected_valid": True,
                    },
                ]
            )

            # Invalid cases
            test_cases.extend(
                [
                    {
                        "description": "Invalid down (too high)",
                        "data": {
                            "down": 5,
                            "distance": 10,
                            "field_position": 25,
                            "quarter": 1,
                            "time_remaining": 3600,
                        },
                        "expected_valid": False,
                    },
                    {
                        "description": "Missing required field",
                        "data": {
                            "distance": 10,
                            "field_position": 25,
                            "quarter": 1,
                            "time_remaining": 3600,
                        },
                        "expected_valid": False,
                    },
                    {
                        "description": "Invalid field position",
                        "data": {
                            "down": 1,
                            "distance": 10,
                            "field_position": 150,
                            "quarter": 1,
                            "time_remaining": 3600,
                        },
                        "expected_valid": False,
                    },
                ]
            )

        elif schema_name == "play_result":
            # Valid cases
            test_cases.extend(
                [
                    {
                        "description": "Valid play result",
                        "data": {
                            "play_id": "play_123",
                            "play_type": "run",
                            "yards_gained": 5,
                            "timestamp": time.time(),
                            "turnover": False,
                            "touchdown": False,
                        },
                        "expected_valid": True,
                    }
                ]
            )

            # Invalid cases
            test_cases.extend(
                [
                    {
                        "description": "Invalid play type",
                        "data": {
                            "play_id": "play_123",
                            "play_type": "invalid_type",
                            "yards_gained": 5,
                            "timestamp": time.time(),
                        },
                        "expected_valid": False,
                    },
                    {
                        "description": "Yards gained out of range",
                        "data": {
                            "play_id": "play_123",
                            "play_type": "run",
                            "yards_gained": 150,
                            "timestamp": time.time(),
                        },
                        "expected_valid": False,
                    },
                ]
            )

        return test_cases


def run_schema_tests():
    """Run comprehensive schema tests."""
    print("Running comprehensive schema tests...")

    schema_manager = SchemaManager()
    test_runner = SchemaTestRunner(schema_manager)

    results = test_runner.run_all_schema_tests()

    print(f"\n=== SCHEMA TEST RESULTS ===")
    print(f"Total schemas tested: {results['total_schemas']}")
    print(f"Passed: {results['passed_schemas']}")
    print(f"Failed: {results['failed_schemas']}")
    print(f"Overall success: {results['overall_success']}")

    # Print detailed results
    for schema_name, schema_result in results["schema_results"].items():
        print(f"\n{schema_name}:")
        print(f"  Success: {schema_result['success']}")
        if not schema_result["success"]:
            print(f"  Errors: {schema_result.get('error_count', 0)}")
            for test_case in schema_result.get("test_cases", []):
                if not test_case["success"]:
                    print(f"    Failed: {test_case['description']}")
                    if test_case["error"]:
                        print(f"      Error: {test_case['error']}")

    return results


if __name__ == "__main__":
    run_schema_tests()
