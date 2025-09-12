#!/usr/bin/env python3
"""
GitHub Copilot Instructions Validator

This script validates that the GitHub Copilot instructions work correctly
by testing all the commands and scenarios described in the instructions.
"""

import os
import sys
import subprocess
import time
from pathlib import Path


class CopilotInstructionValidator:
    """Validates GitHub Copilot instructions by running all suggested commands"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.results = {}
        self.total_tests = 0
        self.passed_tests = 0
    
    def run_validation(self):
        """Run all validation tests"""
        print("🧪 Validating GitHub Copilot Instructions")
        print("=" * 50)
        
        # Test basic functionality
        self.test_syntax_check()
        self.test_core_simulation()
        self.test_individual_play_simulation()
        self.test_core_module_integration()
        self.test_performance_benchmarking()
        
        # Test build and validation steps
        self.test_build_validation_steps()
        
        # Print summary
        self.print_summary()
        
        return self.passed_tests == self.total_tests
    
    def test_syntax_check(self):
        """Test: python3 -m py_compile validators.py main_sim_loop.py simulate_play.py..."""
        print("\n📝 Testing Syntax Check Commands...")
        
        files_to_check = [
            "validators.py", "main_sim_loop.py", "simulate_play.py", 
            "schemas/possession_state.py", "strategic_cognition.py"
        ]
        
        all_passed = True
        for file_path in files_to_check:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                print(f"  ❌ File not found: {file_path}")
                all_passed = False
                continue
            
            try:
                result = subprocess.run([
                    sys.executable, "-m", "py_compile", str(full_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print(f"  ✅ {file_path}: Syntax OK")
                else:
                    print(f"  ❌ {file_path}: Syntax Error - {result.stderr.strip()}")
                    all_passed = False
                    
            except Exception as e:
                print(f"  ❌ {file_path}: Exception - {e}")
                all_passed = False
        
        self._record_test("Syntax Check", all_passed)
    
    def test_core_simulation(self):
        """Test: python3 main_sim_loop.py"""
        print("\n🎮 Testing Core Simulation...")
        
        try:
            start_time = time.time()
            result = subprocess.run([
                sys.executable, str(self.root_dir / "main_sim_loop.py")
            ], capture_output=True, text=True, timeout=30)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            if result.returncode == 0:
                print(f"  ✅ Main simulation runs successfully")
                print(f"  ⏱️ Execution time: {execution_time:.3f} seconds")
                
                # Check if output contains expected play results
                if "Play" in result.stdout:
                    print(f"  ✅ Output contains expected play results")
                    self._record_test("Core Simulation", True)
                else:
                    print(f"  ❌ Output doesn't contain expected play results")
                    print(f"      Output: {result.stdout}")
                    self._record_test("Core Simulation", False)
            else:
                print(f"  ❌ Main simulation failed: {result.stderr}")
                self._record_test("Core Simulation", False)
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ Main simulation timed out (>30 seconds)")
            self._record_test("Core Simulation", False)
        except Exception as e:
            print(f"  ❌ Main simulation exception: {e}")
            self._record_test("Core Simulation", False)
    
    def test_individual_play_simulation(self):
        """Test individual play simulation as described in instructions"""
        print("\n⚡ Testing Individual Play Simulation...")
        
        test_code = '''
from simulate_play import simulate_play
play_call = {'play_type': 'run'}
possession_state = {'down': 1, 'distance': 10}
outcome = simulate_play(play_call, possession_state)
print(f"Play simulation result: {outcome}")
'''
        
        try:
            result = subprocess.run([
                sys.executable, "-c", test_code
            ], capture_output=True, text=True, timeout=10, cwd=self.root_dir)
            
            if result.returncode == 0:
                print(f"  ✅ Individual play simulation works")
                print(f"  📊 Result: {result.stdout.strip()}")
                self._record_test("Individual Play Simulation", True)
            else:
                print(f"  ❌ Individual play simulation failed: {result.stderr}")
                self._record_test("Individual Play Simulation", False)
                
        except Exception as e:
            print(f"  ❌ Individual play simulation exception: {e}")
            self._record_test("Individual Play Simulation", False)
    
    def test_core_module_integration(self):
        """Test core module testing as described in instructions"""
        print("\n🔗 Testing Core Module Integration...")
        
        test_code = '''
from schemas.possession_state import create_possession_state
from strategic_cognition import seed_coach_intelligence

coach_profiles = {"KC": {"name": "Andy Reid", "aggression": 0.65}}
game_context = {"rivalry_score": 0.85, "fan_intensity": 0.92}

possession_state = create_possession_state("KC", "BAL", 0.92, 0.85, True, coach_profiles)
coach_intel = seed_coach_intelligence(possession_state["coach_profile"], game_context)

print("✅ Module integration test passed")
print(f"Possession state keys: {list(possession_state.keys())}")
print(f"Coach intelligence: {coach_intel}")
'''
        
        try:
            result = subprocess.run([
                sys.executable, "-c", test_code
            ], capture_output=True, text=True, timeout=10, cwd=self.root_dir)
            
            if result.returncode == 0:
                print(f"  ✅ Core module integration works")
                print(f"  📊 Integration test output:")
                for line in result.stdout.strip().split('\n'):
                    print(f"      {line}")
                self._record_test("Core Module Integration", True)
            else:
                print(f"  ❌ Core module integration failed: {result.stderr}")
                self._record_test("Core Module Integration", False)
                
        except Exception as e:
            print(f"  ❌ Core module integration exception: {e}")
            self._record_test("Core Module Integration", False)
    
    def test_performance_benchmarking(self):
        """Test performance benchmarking as described in instructions"""
        print("\n🚀 Testing Performance Benchmarking...")
        
        # Simple benchmark: run multiple play simulations
        benchmark_code = '''
import time
from simulate_play import simulate_play

play_call = {'play_type': 'run'}
possession_state = {'down': 1, 'distance': 10}

start_time = time.time()
for i in range(100):  # 100 iterations for quick test
    result = simulate_play(play_call, possession_state)
end_time = time.time()

total_time = end_time - start_time
avg_time_per_play = total_time / 100

print(f"100 play simulations completed in {total_time:.6f} seconds")
print(f"Average time per play: {avg_time_per_play*1000000:.2f} microseconds")

# Check if performance is reasonable (should be very fast)
if avg_time_per_play < 0.01:  # Less than 10ms per play
    print("✅ Performance is acceptable")
else:
    print("⚠️ Performance may be slower than expected")
'''
        
        try:
            result = subprocess.run([
                sys.executable, "-c", benchmark_code
            ], capture_output=True, text=True, timeout=30, cwd=self.root_dir)
            
            if result.returncode == 0:
                print(f"  ✅ Performance benchmarking works")
                for line in result.stdout.strip().split('\n'):
                    print(f"  {line}")
                self._record_test("Performance Benchmarking", True)
            else:
                print(f"  ❌ Performance benchmarking failed: {result.stderr}")
                self._record_test("Performance Benchmarking", False)
                
        except Exception as e:
            print(f"  ❌ Performance benchmarking exception: {e}")
            self._record_test("Performance Benchmarking", False)
    
    def test_build_validation_steps(self):
        """Test the build validation steps mentioned in instructions"""
        print("\n🔨 Testing Build Validation Steps...")
        
        # Test py_compile on key files
        key_files = ["main_sim_loop.py", "simulate_play.py"]
        compile_success = True
        
        for file_path in key_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "py_compile", str(full_path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode != 0:
                        compile_success = False
                        print(f"  ❌ Compilation failed for {file_path}")
                except Exception:
                    compile_success = False
        
        if compile_success:
            print(f"  ✅ All key files compile successfully")
        
        # Test basic simulation as part of validation
        try:
            result = subprocess.run([
                sys.executable, str(self.root_dir / "main_sim_loop.py")
            ], capture_output=True, text=True, timeout=10)
            
            sim_success = result.returncode == 0
            if sim_success:
                print(f"  ✅ Core functionality validation passed")
            else:
                print(f"  ❌ Core functionality validation failed")
        except Exception:
            sim_success = False
            print(f"  ❌ Core functionality validation exception")
        
        overall_success = compile_success and sim_success
        self._record_test("Build Validation Steps", overall_success)
    
    def _record_test(self, test_name: str, passed: bool):
        """Record test result"""
        self.results[test_name] = passed
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("🏁 VALIDATION SUMMARY")
        print("=" * 50)
        
        for test_name, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        print(f"\nOverall: {self.passed_tests}/{self.total_tests} tests passed")
        
        if self.passed_tests == self.total_tests:
            print("🎉 All GitHub Copilot instructions are working correctly!")
        else:
            print("⚠️ Some instructions are not working. Manual review needed.")
            print("\nRecommendations:")
            for test_name, passed in self.results.items():
                if not passed:
                    print(f"  - Fix issues in: {test_name}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    validator = CopilotInstructionValidator(root_dir)
    success = validator.run_validation()
    
    # Save results to file
    with open("copilot_instruction_validation.txt", "w") as f:
        f.write("GitHub Copilot Instruction Validation Results\n")
        f.write("=" * 50 + "\n\n")
        
        for test_name, passed in validator.results.items():
            status = "PASS" if passed else "FAIL"
            f.write(f"{status}: {test_name}\n")
        
        f.write(f"\nOverall: {validator.passed_tests}/{validator.total_tests} tests passed\n")
    
    print(f"\n📄 Results saved to copilot_instruction_validation.txt")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())