"""
Fuzzing framework for testing malformed payloads and robustness.
Tests system resilience against invalid inputs and edge cases.
"""

import json
import random
import string
import time
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
import logging

try:
    from hypothesis import strategies as st

    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False


@dataclass
class FuzzResult:
    """Result of a fuzz test."""

    input_data: Any
    expected_behavior: str
    actual_behavior: str
    success: bool
    error_message: Optional[str]
    execution_time: float
    test_name: str


class PayloadFuzzer:
    """Fuzzes payloads with various malformed inputs."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fuzz_results: List[FuzzResult] = []

    def fuzz_json_payloads(
        self, target_function: Callable, num_tests: int = 100
    ) -> List[FuzzResult]:
        """Fuzz JSON payloads with malformed data."""
        results = []

        for i in range(num_tests):
            # Generate malformed JSON payload
            payload = self._generate_malformed_json()

            start_time = time.time()
            try:
                result = target_function(payload)
                execution_time = time.time() - start_time

                # Function should either handle gracefully or raise expected exception
                fuzz_result = FuzzResult(
                    input_data=payload,
                    expected_behavior="graceful_handling_or_expected_exception",
                    actual_behavior="function_completed",
                    success=True,
                    error_message=None,
                    execution_time=execution_time,
                    test_name=f"json_fuzz_{i}",
                )

            except Exception as e:
                execution_time = time.time() - start_time

                # Check if exception is expected/handled properly
                is_expected = self._is_expected_exception(e)

                fuzz_result = FuzzResult(
                    input_data=payload,
                    expected_behavior="graceful_handling_or_expected_exception",
                    actual_behavior=f"exception: {type(e).__name__}",
                    success=is_expected,
                    error_message=str(e),
                    execution_time=execution_time,
                    test_name=f"json_fuzz_{i}",
                )

            results.append(fuzz_result)
            self.fuzz_results.append(fuzz_result)

        return results

    def fuzz_game_state_payloads(
        self, target_function: Callable, num_tests: int = 50
    ) -> List[FuzzResult]:
        """Fuzz game state payloads with invalid field values."""
        results = []

        for i in range(num_tests):
            # Generate malformed game state
            game_state = self._generate_malformed_game_state()

            start_time = time.time()
            try:
                result = target_function(game_state)
                execution_time = time.time() - start_time

                fuzz_result = FuzzResult(
                    input_data=game_state,
                    expected_behavior="validation_error_or_graceful_handling",
                    actual_behavior="function_completed",
                    success=True,
                    error_message=None,
                    execution_time=execution_time,
                    test_name=f"game_state_fuzz_{i}",
                )

            except Exception as e:
                execution_time = time.time() - start_time
                is_expected = self._is_expected_exception(e)

                fuzz_result = FuzzResult(
                    input_data=game_state,
                    expected_behavior="validation_error_or_graceful_handling",
                    actual_behavior=f"exception: {type(e).__name__}",
                    success=is_expected,
                    error_message=str(e),
                    execution_time=execution_time,
                    test_name=f"game_state_fuzz_{i}",
                )

            results.append(fuzz_result)
            self.fuzz_results.append(fuzz_result)

        return results

    def fuzz_message_payloads(
        self, target_function: Callable, num_tests: int = 50
    ) -> List[FuzzResult]:
        """Fuzz message payloads for messaging system."""
        results = []

        for i in range(num_tests):
            # Generate malformed message payload
            message = self._generate_malformed_message()

            start_time = time.time()
            try:
                result = target_function(message)
                execution_time = time.time() - start_time

                fuzz_result = FuzzResult(
                    input_data=message,
                    expected_behavior="validation_error_or_graceful_handling",
                    actual_behavior="function_completed",
                    success=True,
                    error_message=None,
                    execution_time=execution_time,
                    test_name=f"message_fuzz_{i}",
                )

            except Exception as e:
                execution_time = time.time() - start_time
                is_expected = self._is_expected_exception(e)

                fuzz_result = FuzzResult(
                    input_data=message,
                    expected_behavior="validation_error_or_graceful_handling",
                    actual_behavior=f"exception: {type(e).__name__}",
                    success=is_expected,
                    error_message=str(e),
                    execution_time=execution_time,
                    test_name=f"message_fuzz_{i}",
                )

            results.append(fuzz_result)
            self.fuzz_results.append(fuzz_result)

        return results

    def _generate_malformed_json(self) -> Union[str, Dict, List, None]:
        """Generate various types of malformed JSON data."""
        fuzz_type = random.choice(
            [
                "invalid_json_string",
                "null_values",
                "extreme_numbers",
                "deeply_nested",
                "special_characters",
                "wrong_types",
                "empty_structures",
            ]
        )

        if fuzz_type == "invalid_json_string":
            # Invalid JSON strings
            return random.choice(
                [
                    '{"key": value}',  # Missing quotes
                    '{"key": "value",}',  # Trailing comma
                    '{key: "value"}',  # Unquoted key
                    '{"key": "value"',  # Missing closing brace
                    "not json at all",
                    "",
                    None,
                ]
            )

        elif fuzz_type == "null_values":
            return {
                "required_field": None,
                "another_field": None,
                None: "value",
                "": None,
            }

        elif fuzz_type == "extreme_numbers":
            return {
                "huge_number": 10**308,
                "negative_huge": -(10**308),
                "tiny_number": 10**-308,
                "infinity": float("inf"),
                "negative_infinity": float("-inf"),
                "nan": float("nan"),
            }

        elif fuzz_type == "deeply_nested":
            # Create deeply nested structure
            nested = {"value": 42}
            for i in range(100):  # Very deep nesting
                nested = {"level": i, "data": nested}
            return nested

        elif fuzz_type == "special_characters":
            special_chars = "".join(chr(i) for i in range(32)) + '\\"\r\n\t'
            return {
                special_chars: "value",
                "key": special_chars,
                "unicode": "🏈🎯⚡🔥💥",
                "control_chars": "\x00\x01\x02\x03",
            }

        elif fuzz_type == "wrong_types":
            return {
                "timestamp": "not_a_number",
                "boolean_field": "not_boolean",
                "array_field": "not_an_array",
                "object_field": "not_an_object",
            }

        else:  # empty_structures
            return random.choice([{}, [], "", 0, False])

    def _generate_malformed_game_state(self) -> Dict[str, Any]:
        """Generate malformed game state data."""
        return {
            "down": random.choice([-1, 0, 5, 100, None, "invalid", []]),
            "distance": random.choice([-10, 0, 200, None, "invalid", {}]),
            "field_position": random.choice([-50, 150, None, "invalid", []]),
            "quarter": random.choice([0, 5, -1, None, "invalid", {}]),
            "time_remaining": random.choice([-100, 5000, None, "invalid", []]),
            "score_differential": random.choice([None, "invalid", [], {}]),
            "team": random.choice([None, "", 123, [], {}]),
            "invalid_field": "should_not_exist",
            None: "null_key",
            123: "numeric_key",
        }

    def _generate_malformed_message(self) -> Dict[str, Any]:
        """Generate malformed message data for messaging system."""
        return {
            "message_id": random.choice([None, "", 123, [], {}]),
            "destination": random.choice([None, "", 123, [], {}]),
            "payload": random.choice([None, "not_dict", 123, []]),
            "priority": random.choice([None, "invalid", -1, 10, []]),
            "schema_name": random.choice([None, "", 123, [], {}]),
            "timestamp": random.choice([None, "invalid", -1, []]),
            "invalid_field": random.choice([{}, [], None, ""]),
            "": "empty_key",
            123: "numeric_key",
        }

    def _is_expected_exception(self, exception: Exception) -> bool:
        """Check if an exception is expected/properly handled."""
        expected_exceptions = [
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            json.JSONDecodeError,
            # Add custom exceptions from your codebase
        ]

        return any(isinstance(exception, exc_type) for exc_type in expected_exceptions)

    def generate_fuzz_report(self) -> Dict[str, Any]:
        """Generate a comprehensive fuzz testing report."""
        if not self.fuzz_results:
            return {"error": "No fuzz results available"}

        total_tests = len(self.fuzz_results)
        successful_tests = sum(1 for r in self.fuzz_results if r.success)

        # Group by test type
        test_types = {}
        for result in self.fuzz_results:
            test_type = result.test_name.split("_")[0]
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "success": 0, "failures": []}

            test_types[test_type]["total"] += 1
            if result.success:
                test_types[test_type]["success"] += 1
            else:
                test_types[test_type]["failures"].append(
                    {
                        "test_name": result.test_name,
                        "error": result.error_message,
                        "input": str(result.input_data)[
                            :200
                        ],  # Truncate for readability
                    }
                )

        # Performance analysis
        avg_execution_time = (
            sum(r.execution_time for r in self.fuzz_results) / total_tests
        )
        max_execution_time = max(r.execution_time for r in self.fuzz_results)

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": total_tests - successful_tests,
                "success_rate": successful_tests / total_tests * 100,
                "avg_execution_time": avg_execution_time,
                "max_execution_time": max_execution_time,
            },
            "test_types": test_types,
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on fuzz test results."""
        recommendations = []

        failed_tests = [r for r in self.fuzz_results if not r.success]

        if len(failed_tests) > len(self.fuzz_results) * 0.1:  # More than 10% failure
            recommendations.append(
                "High failure rate detected. Consider improving input validation."
            )

        # Check for specific patterns
        crash_patterns = {}
        for result in failed_tests:
            if result.error_message:
                error_type = result.error_message.split(":")[0]
                crash_patterns[error_type] = crash_patterns.get(error_type, 0) + 1

        for error_type, count in crash_patterns.items():
            if count > 5:
                recommendations.append(
                    f"Multiple {error_type} errors detected. Consider adding specific handling."
                )

        # Performance recommendations
        slow_tests = [r for r in self.fuzz_results if r.execution_time > 1.0]
        if slow_tests:
            recommendations.append(
                f"{len(slow_tests)} tests took longer than 1 second. Consider performance optimization."
            )

        if not recommendations:
            recommendations.append(
                "Fuzz testing passed with good results. System shows good resilience."
            )

        return recommendations


class RegressionTester:
    """Tests against real play-by-play data for regression detection."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.baseline_results: Dict[str, Any] = {}
        self.current_results: Dict[str, Any] = {}

    def load_baseline_data(self, baseline_file: str):
        """Load baseline test results."""
        try:
            with open(baseline_file, "r") as f:
                self.baseline_results = json.load(f)
            self.logger.info(f"Loaded baseline from {baseline_file}")
        except Exception as e:
            self.logger.error(f"Failed to load baseline: {e}")

    def run_regression_tests(
        self, test_data: List[Dict[str, Any]], target_function: Callable
    ) -> Dict[str, Any]:
        """Run regression tests against historical data."""
        results = {
            "tests_run": 0,
            "regressions_detected": 0,
            "performance_changes": [],
            "output_changes": [],
            "new_errors": [],
        }

        for i, test_case in enumerate(test_data):
            test_id = f"regression_test_{i}"

            try:
                start_time = time.time()
                output = target_function(test_case)
                execution_time = time.time() - start_time

                # Store current result
                self.current_results[test_id] = {
                    "output": output,
                    "execution_time": execution_time,
                    "success": True,
                }

                # Compare with baseline if available
                if test_id in self.baseline_results:
                    baseline = self.baseline_results[test_id]

                    # Check for output changes
                    if self._outputs_differ(baseline.get("output"), output):
                        results["output_changes"].append(
                            {
                                "test_id": test_id,
                                "baseline_output": baseline.get("output"),
                                "current_output": output,
                            }
                        )
                        results["regressions_detected"] += 1

                    # Check for performance changes
                    baseline_time = baseline.get("execution_time", 0)
                    if execution_time > baseline_time * 1.5:  # 50% slower
                        results["performance_changes"].append(
                            {
                                "test_id": test_id,
                                "baseline_time": baseline_time,
                                "current_time": execution_time,
                                "change_percent": (execution_time - baseline_time)
                                / baseline_time
                                * 100,
                            }
                        )

                results["tests_run"] += 1

            except Exception as e:
                # Store error result
                self.current_results[test_id] = {"error": str(e), "success": False}

                # Check if this is a new error
                if test_id in self.baseline_results and self.baseline_results[
                    test_id
                ].get("success", False):
                    results["new_errors"].append({"test_id": test_id, "error": str(e)})
                    results["regressions_detected"] += 1

                results["tests_run"] += 1

        return results

    def save_current_as_baseline(self, baseline_file: str):
        """Save current results as new baseline."""
        try:
            with open(baseline_file, "w") as f:
                json.dump(self.current_results, f, indent=2, default=str)
            self.logger.info(f"Saved baseline to {baseline_file}")
        except Exception as e:
            self.logger.error(f"Failed to save baseline: {e}")

    def _outputs_differ(self, baseline_output: Any, current_output: Any) -> bool:
        """Check if outputs differ significantly."""
        # Simple comparison - could be enhanced for specific data types
        try:
            return str(baseline_output) != str(current_output)
        except:
            return True


def run_comprehensive_fuzz_tests():
    """Run comprehensive fuzz testing suite."""
    print("Starting comprehensive fuzz testing...")

    fuzzer = PayloadFuzzer()

    # Define simple test functions
    def dummy_json_processor(data):
        if isinstance(data, str):
            return json.loads(data)
        return data

    def dummy_game_state_processor(state):
        if not isinstance(state, dict):
            raise ValueError("State must be dictionary")

        required_fields = ["down", "distance", "field_position"]
        for field in required_fields:
            if field not in state:
                raise ValueError(f"Missing required field: {field}")
            if not isinstance(state[field], (int, float)):
                raise TypeError(f"Field {field} must be numeric")

        return {"processed": True, "state": state}

    # Run fuzz tests
    print("Running JSON payload fuzz tests...")
    json_results = fuzzer.fuzz_json_payloads(dummy_json_processor, 20)

    print("Running game state fuzz tests...")
    state_results = fuzzer.fuzz_game_state_payloads(dummy_game_state_processor, 20)

    # Generate report
    report = fuzzer.generate_fuzz_report()

    print("\n=== FUZZ TEST REPORT ===")
    print(f"Total tests: {report['summary']['total_tests']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print(f"Average execution time: {report['summary']['avg_execution_time']:.4f}s")

    print("\nRecommendations:")
    for rec in report["recommendations"]:
        print(f"  - {rec}")

    return report


if __name__ == "__main__":
    run_comprehensive_fuzz_tests()
