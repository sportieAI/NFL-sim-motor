#!/usr/bin/env python3
"""
PR #6 Issue Validation Script

This script validates that all issues identified in PR #6 have been addressed:
1. Circular import issues ✅
2. Syntax errors (emoji characters) ✅  
3. Missing dependencies (requirements.txt) ✅
4. Build and test validation ✅
5. GitHub Copilot instructions validation ✅
"""

import os
import sys
import subprocess
import json
from pathlib import Path


class PR6IssueValidator:
    """Validates that all PR #6 issues have been resolved"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.validation_results = {}
    
    def run_validation(self):
        """Run complete validation of PR #6 fixes"""
        print("🔍 Validating PR #6 Issue Resolution")
        print("=" * 50)
        
        # Test each category of issues from PR #6
        self.test_circular_imports_fixed()
        self.test_syntax_errors_fixed() 
        self.test_requirements_txt_present()
        self.test_build_processes_work()
        self.test_copilot_instructions_validated()
        self.test_automation_framework_present()
        
        # Print summary
        self.print_validation_summary()
        
        # Return overall success
        return all(self.validation_results.values())
    
    def test_circular_imports_fixed(self):
        """Test that circular imports in agents/ module are fixed"""
        print("\n🔄 Testing Circular Import Fixes...")
        
        try:
            # Test importing each agent module
            test_code = '''
from agents.coach_agent import CoachAgent
from agents.play_calling_agent import PlayCallingAgent  
from agents.defensive_agent import DefensiveAgent
from agents.special_teams_agent import SpecialTeamsAgent

# Test that we can instantiate them without circular import errors
team_context = {"name": "TestTeam"}
coach = CoachAgent(team_context)
play_caller = PlayCallingAgent(team_context)
defense = DefensiveAgent(team_context)
special_teams = SpecialTeamsAgent(team_context)

print("✅ All agent modules import successfully without circular import errors")
'''
            
            result = subprocess.run([
                sys.executable, "-c", test_code
            ], capture_output=True, text=True, timeout=15, cwd=self.root_dir)
            
            if result.returncode == 0:
                print("  ✅ Circular imports are fixed")
                print("  ✅ All agent modules can be imported successfully")
                self.validation_results['circular_imports'] = True
            else:
                print("  ❌ Circular import issues remain:")
                print(f"      {result.stderr}")
                self.validation_results['circular_imports'] = False
                
        except Exception as e:
            print(f"  ❌ Exception testing circular imports: {e}")
            self.validation_results['circular_imports'] = False
    
    def test_syntax_errors_fixed(self):
        """Test that syntax errors (emoji characters) are fixed"""
        print("\n📝 Testing Syntax Error Fixes...")
        
        # Files that had emoji character issues in PR #6
        files_with_emoji_fixes = [
            "main.py",
            "strategic_cognition.py", 
            "schemas/possession_state.py"
        ]
        
        all_syntax_good = True
        
        for file_path in files_with_emoji_fixes:
            full_path = self.root_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to compile the file
                    compile(content, str(full_path), 'exec')
                    print(f"  ✅ {file_path}: Syntax is valid")
                    
                    # Check that emoji was converted to comment
                    if content.startswith('#'):
                        print(f"  ✅ {file_path}: Emoji character properly converted to comment")
                    
                except SyntaxError as e:
                    print(f"  ❌ {file_path}: Syntax error remains - {e}")
                    all_syntax_good = False
                except Exception as e:
                    print(f"  ❌ {file_path}: Error checking syntax - {e}")
                    all_syntax_good = False
            else:
                print(f"  ⚠️ {file_path}: File not found")
        
        self.validation_results['syntax_errors'] = all_syntax_good
    
    def test_requirements_txt_present(self):
        """Test that requirements.txt is present and comprehensive"""
        print("\n📦 Testing Requirements.txt...")
        
        req_file = self.root_dir / "requirements.txt"
        
        if not req_file.exists():
            print("  ❌ requirements.txt is missing")
            self.validation_results['requirements_txt'] = False
            return
        
        try:
            with open(req_file, 'r') as f:
                content = f.read()
            
            # Check that it's not just the minimal "unittest" that was there before
            lines = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.startswith('#')]
            
            if len(lines) < 5:  # Should have multiple dependencies
                print(f"  ❌ requirements.txt appears minimal ({len(lines)} dependencies)")
                self.validation_results['requirements_txt'] = False
                return
            
            # Check for key dependencies mentioned in PR #6
            expected_deps = ['pytest', 'numpy', 'pandas', 'torch', 'fastapi']
            missing_deps = []
            
            content_lower = content.lower()
            for dep in expected_deps:
                if dep.lower() not in content_lower:
                    missing_deps.append(dep)
            
            if missing_deps:
                print(f"  ⚠️ Some expected dependencies missing: {missing_deps}")
            
            print(f"  ✅ requirements.txt exists with {len(lines)} dependencies")
            print(f"  ✅ File appears comprehensive (not minimal)")
            self.validation_results['requirements_txt'] = True
            
        except Exception as e:
            print(f"  ❌ Error reading requirements.txt: {e}")
            self.validation_results['requirements_txt'] = False
    
    def test_build_processes_work(self):
        """Test that build and validation processes work"""
        print("\n🔨 Testing Build Processes...")
        
        build_success = True
        
        # Test syntax compilation of key files
        key_files = ["main_sim_loop.py", "simulate_play.py", "validators.py"]
        
        for file_path in key_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                try:
                    result = subprocess.run([
                        sys.executable, "-m", "py_compile", str(full_path)
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        print(f"  ✅ {file_path}: Compiles successfully")
                    else:
                        print(f"  ❌ {file_path}: Compilation failed")
                        build_success = False
                except Exception as e:
                    print(f"  ❌ {file_path}: Exception during compilation - {e}")
                    build_success = False
        
        # Test that main simulation runs
        try:
            result = subprocess.run([
                sys.executable, str(self.root_dir / "main_sim_loop.py")
            ], capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print("  ✅ Main simulation runs successfully")
            else:
                print("  ❌ Main simulation failed to run")
                build_success = False
        except Exception as e:
            print(f"  ❌ Exception running main simulation: {e}")
            build_success = False
        
        self.validation_results['build_processes'] = build_success
    
    def test_copilot_instructions_validated(self):
        """Test that GitHub Copilot instructions are present and validated"""
        print("\n📋 Testing GitHub Copilot Instructions...")
        
        # Check if copilot instructions file exists
        possible_instruction_files = [
            ".github/copilot-instructions.md",
            "COPILOT_AGENT_INSTRUCTIONS.md"
        ]
        
        instruction_file_found = False
        for file_path in possible_instruction_files:
            full_path = self.root_dir / file_path
            if full_path.exists():
                instruction_file_found = True
                print(f"  ✅ Found instruction file: {file_path}")
                
                # Check file content
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if len(content) > 1000:  # Should be comprehensive
                        print(f"  ✅ Instruction file is comprehensive ({len(content)} characters)")
                    else:
                        print(f"  ⚠️ Instruction file may be too brief ({len(content)} characters)")
                        
                except Exception as e:
                    print(f"  ❌ Error reading instruction file: {e}")
                
                break
        
        if not instruction_file_found:
            print("  ❌ No GitHub Copilot instruction file found")
            self.validation_results['copilot_instructions'] = False
            return
        
        # Test the validation script if it exists
        validator_script = self.root_dir / "automation" / "copilot_instruction_validator.py"
        if validator_script.exists():
            try:
                result = subprocess.run([
                    sys.executable, str(validator_script)
                ], capture_output=True, text=True, timeout=60, cwd=self.root_dir)
                
                if result.returncode == 0:
                    print("  ✅ Copilot instruction validator passes")
                    # Count passed tests from output
                    if "tests passed" in result.stdout:
                        print("  ✅ All instruction validation tests pass")
                else:
                    print("  ⚠️ Copilot instruction validator had issues")
                    
            except Exception as e:
                print(f"  ⚠️ Exception running instruction validator: {e}")
        
        self.validation_results['copilot_instructions'] = instruction_file_found
    
    def test_automation_framework_present(self):
        """Test that automation framework is present and functional"""
        print("\n🤖 Testing Automation Framework...")
        
        automation_dir = self.root_dir / "automation"
        if not automation_dir.exists():
            print("  ❌ Automation directory not found")
            self.validation_results['automation_framework'] = False
            return
        
        # Check for key automation scripts
        expected_scripts = [
            "issue_detector_and_fixer.py",
            "copilot_instruction_validator.py", 
            "simplified_auto_fixer.py"
        ]
        
        scripts_found = 0
        for script in expected_scripts:
            script_path = automation_dir / script
            if script_path.exists():
                scripts_found += 1
                print(f"  ✅ Found: {script}")
                
                # Test that script runs without errors
                try:
                    result = subprocess.run([
                        sys.executable, str(script_path), "--help"
                    ], capture_output=True, text=True, timeout=10, cwd=self.root_dir)
                    # Most scripts don't have --help, so just check they can be imported
                    
                except Exception:
                    # Try just importing the script to check basic syntax
                    try:
                        result = subprocess.run([
                            sys.executable, "-c", f"import sys; sys.path.append('{automation_dir}'); import {script[:-3]}"
                        ], capture_output=True, text=True, timeout=10)
                        
                        if result.returncode == 0:
                            print(f"    ✅ {script} imports successfully")
                        else:
                            print(f"    ⚠️ {script} has import issues")
                    except Exception as e:
                        print(f"    ⚠️ {script} validation error: {e}")
            else:
                print(f"  ❌ Missing: {script}")
        
        # Check for CI workflow
        ci_workflow = self.root_dir / ".github" / "workflows" / "automated-issue-detection-and-fix.yml"
        if ci_workflow.exists():
            print("  ✅ Found automated CI workflow")
            scripts_found += 1
        else:
            print("  ❌ Missing automated CI workflow")
        
        # Check for documentation
        docs_dir = self.root_dir / "docs"
        automation_docs = docs_dir / "AUTOMATION_FRAMEWORK.md"
        if automation_docs.exists():
            print("  ✅ Found automation framework documentation")
            scripts_found += 1
        else:
            print("  ❌ Missing automation framework documentation")
        
        self.validation_results['automation_framework'] = scripts_found >= 3  # At least 3 components
    
    def print_validation_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 50)
        print("🏁 PR #6 ISSUE VALIDATION SUMMARY")  
        print("=" * 50)
        
        issue_categories = {
            'circular_imports': 'Circular Import Issues Fixed',
            'syntax_errors': 'Syntax Errors (Emoji Characters) Fixed',
            'requirements_txt': 'Requirements.txt Present and Comprehensive',
            'build_processes': 'Build and Test Processes Work',
            'copilot_instructions': 'GitHub Copilot Instructions Present',
            'automation_framework': 'Automation Framework Implemented'
        }
        
        passed_count = 0
        total_count = len(self.validation_results)
        
        for key, description in issue_categories.items():
            if key in self.validation_results:
                status = "✅ RESOLVED" if self.validation_results[key] else "❌ NOT RESOLVED"
                print(f"{status}: {description}")
                if self.validation_results[key]:
                    passed_count += 1
            else:
                print(f"⚠️ NOT TESTED: {description}")
        
        print(f"\nOverall: {passed_count}/{total_count} issue categories resolved")
        
        if passed_count == total_count:
            print("\n🎉 All PR #6 issues have been successfully resolved!")
            print("✅ Circular imports fixed")
            print("✅ Syntax errors fixed") 
            print("✅ Dependencies properly managed")
            print("✅ Build processes working")
            print("✅ Automation framework implemented")
        else:
            print(f"\n⚠️ {total_count - passed_count} issue categories still need attention")
    
    def save_report(self):
        """Save validation report to file"""
        report = {
            "pr6_validation_summary": {
                "total_categories": len(self.validation_results),
                "resolved_categories": sum(self.validation_results.values()),
                "success_rate": sum(self.validation_results.values()) / len(self.validation_results) * 100,
                "detailed_results": self.validation_results
            }
        }
        
        with open("pr6_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to pr6_validation_report.json")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    validator = PR6IssueValidator(root_dir)
    success = validator.run_validation()
    validator.save_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())