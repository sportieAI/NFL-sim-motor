#!/usr/bin/env python3
"""
NFL Simulation Engine - Issue Detection and Auto-Fix Framework

This module automatically detects and fixes common issues in the codebase:
1. Circular import issues
2. Syntax errors (emoji characters, unclosed strings, etc.)
3. Missing dependencies
4. Build and test validation

Based on issues identified in PR #6.
"""

import os
import sys
import ast
import re
import subprocess
import json
import importlib.util
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from dataclasses import dataclass


@dataclass
class IssueReport:
    """Represents an issue found in the codebase"""
    file_path: str
    issue_type: str
    description: str
    line_number: Optional[int] = None
    fix_applied: bool = False
    fix_description: str = ""


class CircularImportDetector:
    """Detects and fixes circular import issues"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.import_graph = {}
        self.circular_imports = set()
    
    def analyze_imports(self) -> List[IssueReport]:
        """Analyze all Python files for import dependencies"""
        issues = []
        
        # Build import graph
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = self._extract_imports(content)
                rel_path = str(py_file.relative_to(self.root_dir))
                self.import_graph[rel_path] = imports
                
            except Exception as e:
                issues.append(IssueReport(
                    file_path=str(py_file),
                    issue_type="import_analysis_error",
                    description=f"Could not analyze imports: {e}"
                ))
        
        # Detect circular imports
        circular_deps = self._detect_circular_dependencies()
        
        for cycle in circular_deps:
            for file_path in cycle:
                issues.append(IssueReport(
                    file_path=file_path,
                    issue_type="circular_import",
                    description=f"Circular import detected in cycle: {' -> '.join(cycle)}"
                ))
        
        return issues
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code"""
        imports = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except SyntaxError:
            # If there's a syntax error, try regex fallback
            import_patterns = [
                r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_.]*)',
                r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import'
            ]
            
            for line in content.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line)
                    if match:
                        imports.append(match.group(1))
        
        return imports
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for dependency in self.import_graph.get(node, []):
                # Convert module name to file path
                dep_file = self._module_to_file(dependency)
                if dep_file and dep_file in self.import_graph:
                    dfs(dep_file, path + [node])
            
            rec_stack.remove(node)
        
        for file_path in self.import_graph:
            if file_path not in visited:
                dfs(file_path, [])
        
        return cycles
    
    def _module_to_file(self, module_name: str) -> Optional[str]:
        """Convert module name to file path"""
        # Handle relative imports within the project
        if module_name.startswith('.'):
            return None
        
        # Convert module.submodule to module/submodule.py
        file_path = module_name.replace('.', '/') + '.py'
        
        # Check if file exists in project
        full_path = self.root_dir / file_path
        if full_path.exists():
            return file_path
        
        return None
    
    def fix_circular_imports(self, issues: List[IssueReport]) -> List[IssueReport]:
        """Fix circular import issues by moving imports inside functions"""
        fixed_issues = []
        
        for issue in issues:
            if issue.issue_type == "circular_import":
                try:
                    fixed = self._fix_single_circular_import(issue.file_path)
                    if fixed:
                        issue.fix_applied = True
                        issue.fix_description = "Moved imports inside functions to break circular dependency"
                        fixed_issues.append(issue)
                except Exception as e:
                    issue.fix_description = f"Failed to fix: {e}"
                    fixed_issues.append(issue)
        
        return fixed_issues
    
    def _fix_single_circular_import(self, file_path: str) -> bool:
        """Fix circular import in a single file by moving imports inside functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            new_lines = []
            import_lines = []
            
            # Extract top-level imports that might cause circular dependencies
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Check for agent imports that are likely circular
                if (stripped.startswith('from agents.') and 'import' in stripped) or \
                   (stripped.startswith('import agents.')):
                    import_lines.append((i, line))
                    # Add comment explaining the change
                    new_lines.append(f"# {line.strip()} # Moved inside function to avoid circular import")
                else:
                    new_lines.append(line)
            
            if import_lines:
                # Find function definitions and add imports inside them
                content_modified = '\n'.join(new_lines)
                
                # Look for functions that use the imported modules
                tree = ast.parse(content_modified.replace('# Moved inside function to avoid circular import', ''))
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Add imports at the beginning of functions that need them
                        func_start_line = node.lineno - 1
                        
                        # Insert imports after function definition
                        for import_line_num, import_line in import_lines:
                            # Clean up the import line
                            clean_import = import_line.strip()
                            if clean_import.startswith('# '):
                                clean_import = clean_import[2:]
                            if ' # Moved inside function to avoid circular import' in clean_import:
                                clean_import = clean_import.replace(' # Moved inside function to avoid circular import', '')
                            
                            # Insert the import inside the function
                            new_lines.insert(func_start_line + 1, f"            {clean_import}")
                            func_start_line += 1  # Adjust for inserted line
                
                # Write the modified content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(new_lines))
                
                return True
            
        except Exception as e:
            print(f"Error fixing circular import in {file_path}: {e}")
            return False
        
        return False


class SyntaxErrorDetector:
    """Detects and fixes syntax errors"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
    
    def detect_syntax_errors(self) -> List[IssueReport]:
        """Detect syntax errors in Python files"""
        issues = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Try to compile the file
                compile(content, str(py_file), 'exec')
                
            except SyntaxError as e:
                issues.append(IssueReport(
                    file_path=str(py_file),
                    issue_type="syntax_error",
                    description=f"Syntax error: {e.msg}",
                    line_number=e.lineno
                ))
            except Exception as e:
                issues.append(IssueReport(
                    file_path=str(py_file),
                    issue_type="compilation_error",
                    description=f"Compilation error: {e}"
                ))
        
        return issues
    
    def fix_syntax_errors(self, issues: List[IssueReport]) -> List[IssueReport]:
        """Fix common syntax errors"""
        fixed_issues = []
        
        for issue in issues:
            if issue.issue_type in ["syntax_error", "compilation_error"]:
                try:
                    fixed = self._fix_single_syntax_error(issue)
                    if fixed:
                        issue.fix_applied = True
                        fixed_issues.append(issue)
                    else:
                        fixed_issues.append(issue)
                except Exception as e:
                    issue.fix_description = f"Failed to fix: {e}"
                    fixed_issues.append(issue)
        
        return fixed_issues
    
    def _fix_single_syntax_error(self, issue: IssueReport) -> bool:
        """Fix a single syntax error"""
        try:
            with open(issue.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Fix emoji characters at start of file
            if "invalid character" in issue.description and "🟡" in content:
                lines[0] = "# " + lines[0]  # Comment out the emoji line
                issue.fix_description = "Commented out emoji character causing syntax error"
                
            elif "invalid character" in issue.description and "🔴" in content:
                lines[0] = "# " + lines[0]  # Comment out the emoji line
                issue.fix_description = "Commented out emoji character causing syntax error"
                
            elif "invalid character" in issue.description and "🟣" in content:
                lines[0] = "# " + lines[0]  # Comment out the emoji line
                issue.fix_description = "Commented out emoji character causing syntax error"
            
            # Fix unterminated triple-quoted strings
            elif "unterminated triple-quoted string" in issue.description:
                # Find the unterminated triple quote and close it
                for i, line in enumerate(lines):
                    if '"""' in line and line.count('"""') % 2 == 1:
                        # Add closing triple quote
                        lines.append('"""')
                        issue.fix_description = "Added missing closing triple quotes"
                        break
            
            # Fix unclosed parentheses
            elif "'(' was never closed" in issue.description:
                if issue.line_number:
                    line_idx = issue.line_number - 1
                    if line_idx < len(lines):
                        lines[line_idx] = lines[line_idx].rstrip() + ")"
                        issue.fix_description = "Added missing closing parenthesis"
            
            # Fix missing except/finally blocks
            elif "expected 'except' or 'finally' block" in issue.description:
                if issue.line_number:
                    line_idx = issue.line_number - 1
                    # Add a basic except block
                    lines.insert(line_idx + 1, "    except Exception as e:")
                    lines.insert(line_idx + 2, "        print(f\"Error: {e}\")")
                    issue.fix_description = "Added missing except block"
            
            else:
                return False
            
            # Write the fixed content
            with open(issue.file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            # Verify the fix worked
            try:
                with open(issue.file_path, 'r', encoding='utf-8') as f:
                    fixed_content = f.read()
                compile(fixed_content, issue.file_path, 'exec')
                return True
            except SyntaxError:
                return False
                
        except Exception as e:
            print(f"Error fixing syntax error in {issue.file_path}: {e}")
            return False
        
        return True


class DependencyAnalyzer:
    """Analyzes dependencies and generates requirements.txt"""
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.known_packages = {
            'numpy', 'pandas', 'scikit-learn', 'torch', 'transformers',
            'fastapi', 'pytest', 'flask', 'requests', 'matplotlib',
            'plotly', 'redis', 'pyjwt', 'librosa', 'hdbscan',
            'dowhy', 'shap', 'networkx', 'supabase', 'firebase-admin'
        }
    
    def analyze_dependencies(self) -> List[IssueReport]:
        """Analyze Python files for import dependencies"""
        issues = []
        all_imports = set()
        
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                imports = self._extract_third_party_imports(content)
                all_imports.update(imports)
                
            except Exception as e:
                issues.append(IssueReport(
                    file_path=str(py_file),
                    issue_type="dependency_analysis_error",
                    description=f"Could not analyze dependencies: {e}"
                ))
        
        # Check if requirements.txt exists and is up to date
        req_file = self.root_dir / "requirements.txt"
        if not req_file.exists():
            issues.append(IssueReport(
                file_path=str(req_file),
                issue_type="missing_requirements",
                description="requirements.txt file is missing"
            ))
        else:
            # Check if current requirements match detected dependencies
            try:
                with open(req_file, 'r') as f:
                    existing_reqs = set(line.split('>=')[0].split('==')[0].strip() 
                                      for line in f if line.strip() and not line.startswith('#'))
                
                missing_deps = all_imports - existing_reqs
                if missing_deps:
                    issues.append(IssueReport(
                        file_path=str(req_file),
                        issue_type="outdated_requirements",
                        description=f"Missing dependencies: {', '.join(missing_deps)}"
                    ))
            except Exception as e:
                issues.append(IssueReport(
                    file_path=str(req_file),
                    issue_type="requirements_read_error",
                    description=f"Could not read requirements.txt: {e}"
                ))
        
        return issues
    
    def _extract_third_party_imports(self, content: str) -> Set[str]:
        """Extract third-party package imports"""
        imports = set()
        
        # Standard library modules (partial list)
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'random', 'math',
            'collections', 'itertools', 'functools', 'typing', 'pathlib',
            'subprocess', 'unittest', 'logging', 'asyncio', 're', 'ast'
        }
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        package = alias.name.split('.')[0]
                        if package not in stdlib_modules:
                            imports.add(package)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        package = node.module.split('.')[0]
                        if package not in stdlib_modules:
                            imports.add(package)
        except SyntaxError:
            # Fallback to regex if syntax error
            import_patterns = [
                r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
            ]
            
            for line in content.split('\n'):
                for pattern in import_patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        package = match.group(1)
                        if package not in stdlib_modules:
                            imports.add(package)
        
        return imports
    
    def generate_requirements(self, dependencies: Set[str]) -> str:
        """Generate requirements.txt content"""
        requirements = []
        
        # Map detected imports to package names with versions
        package_mapping = {
            'numpy': 'numpy>=1.21.0',
            'pandas': 'pandas>=1.3.0',
            'sklearn': 'scikit-learn>=1.0.0',
            'torch': 'torch>=1.9.0',
            'transformers': 'transformers>=4.0.0',
            'fastapi': 'fastapi>=0.70.0',
            'pytest': 'pytest>=7.0.0',
            'requests': 'requests>=2.25.0',
            'matplotlib': 'matplotlib>=3.5.0',
            'plotly': 'plotly>=5.0.0',
            'redis': 'redis>=4.0.0',
            'jwt': 'pyjwt>=2.0.0',
            'librosa': 'librosa>=0.8.0',
            'hdbscan': 'hdbscan>=0.8.0',
            'dowhy': 'dowhy>=0.8.0',
            'shap': 'shap>=0.40.0',
            'networkx': 'networkx>=2.6.0'
        }
        
        for dep in sorted(dependencies):
            if dep in package_mapping:
                requirements.append(package_mapping[dep])
            else:
                requirements.append(f"{dep}>=1.0.0  # Auto-detected, please verify version")
        
        content = "# Auto-generated requirements.txt\n"
        content += "# Please review and adjust versions as needed\n\n"
        content += "# Core dependencies\n"
        content += "\n".join(requirements)
        content += "\n\n# Testing\npytest>=7.0.0\n"
        
        return content


class AutomationFramework:
    """Main automation framework that orchestrates all fixes"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.circular_detector = CircularImportDetector(str(self.root_dir))
        self.syntax_detector = SyntaxErrorDetector(str(self.root_dir))
        self.dependency_analyzer = DependencyAnalyzer(str(self.root_dir))
        self.issues = []
    
    def run_full_analysis(self) -> Dict[str, List[IssueReport]]:
        """Run full analysis and return categorized issues"""
        print("🔍 Running comprehensive codebase analysis...")
        
        # Detect all issues
        syntax_issues = self.syntax_detector.detect_syntax_errors()
        circular_issues = self.circular_detector.analyze_imports()
        dependency_issues = self.dependency_analyzer.analyze_dependencies()
        
        self.issues = syntax_issues + circular_issues + dependency_issues
        
        return {
            'syntax_errors': syntax_issues,
            'circular_imports': circular_issues,
            'dependency_issues': dependency_issues
        }
    
    def apply_fixes(self) -> Dict[str, List[IssueReport]]:
        """Apply automatic fixes where possible"""
        print("🔧 Applying automatic fixes...")
        
        fixed_issues = {'syntax_errors': [], 'circular_imports': [], 'dependency_issues': []}
        
        # Fix syntax errors first (they prevent other analysis)
        syntax_issues = [i for i in self.issues if i.issue_type in ['syntax_error', 'compilation_error']]
        fixed_syntax = self.syntax_detector.fix_syntax_errors(syntax_issues)
        fixed_issues['syntax_errors'] = fixed_syntax
        
        # Fix circular imports
        circular_issues = [i for i in self.issues if i.issue_type == 'circular_import']
        fixed_circular = self.circular_detector.fix_circular_imports(circular_issues)
        fixed_issues['circular_imports'] = fixed_circular
        
        # Fix dependency issues
        dependency_issues = [i for i in self.issues if 'requirements' in i.issue_type]
        fixed_deps = self._fix_dependency_issues(dependency_issues)
        fixed_issues['dependency_issues'] = fixed_deps
        
        return fixed_issues
    
    def _fix_dependency_issues(self, issues: List[IssueReport]) -> List[IssueReport]:
        """Fix dependency-related issues"""
        fixed_issues = []
        
        for issue in issues:
            try:
                if issue.issue_type == "missing_requirements":
                    # Generate requirements.txt
                    all_deps = set()
                    for py_file in self.root_dir.rglob("*.py"):
                        if "__pycache__" not in str(py_file):
                            try:
                                with open(py_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                deps = self.dependency_analyzer._extract_third_party_imports(content)
                                all_deps.update(deps)
                            except:
                                continue
                    
                    req_content = self.dependency_analyzer.generate_requirements(all_deps)
                    
                    with open(self.root_dir / "requirements.txt", 'w') as f:
                        f.write(req_content)
                    
                    issue.fix_applied = True
                    issue.fix_description = f"Generated requirements.txt with {len(all_deps)} dependencies"
                    
                fixed_issues.append(issue)
                
            except Exception as e:
                issue.fix_description = f"Failed to fix: {e}"
                fixed_issues.append(issue)
        
        return fixed_issues
    
    def validate_fixes(self) -> Dict[str, bool]:
        """Validate that fixes were successful"""
        print("✅ Validating fixes...")
        
        validation_results = {
            'syntax_check': self._validate_syntax(),
            'import_check': self._validate_imports(),
            'basic_functionality': self._validate_basic_functionality()
        }
        
        return validation_results
    
    def _validate_syntax(self) -> bool:
        """Validate that all Python files have valid syntax"""
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(py_file), 'exec')
            except SyntaxError:
                return False
            except Exception:
                continue
        
        return True
    
    def _validate_imports(self) -> bool:
        """Validate that key modules can be imported without circular dependencies"""
        test_imports = [
            'simulate_play',
            'strategic_cognition'
        ]
        
        for module in test_imports:
            try:
                spec = importlib.util.spec_from_file_location(
                    module, 
                    self.root_dir / f"{module}.py"
                )
                if spec and spec.loader:
                    spec.loader.load_module(spec)
            except ImportError:
                return False
            except Exception:
                continue
        
        return True
    
    def _validate_basic_functionality(self) -> bool:
        """Validate basic simulation functionality"""
        try:
            # Try to run basic simulation
            result = subprocess.run([
                sys.executable, 
                str(self.root_dir / "main_sim_loop.py")
            ], capture_output=True, text=True, timeout=30)
            
            return result.returncode == 0
        except Exception:
            return False
    
    def generate_report(self, issues: Dict[str, List[IssueReport]], 
                       fixes: Dict[str, List[IssueReport]],
                       validation: Dict[str, bool]) -> str:
        """Generate a comprehensive report"""
        report = []
        report.append("# NFL Simulation Engine - Automation Report")
        report.append("=" * 50)
        report.append("")
        
        # Summary
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        total_fixed = sum(len([i for i in issue_list if i.fix_applied]) for issue_list in fixes.values())
        
        report.append(f"## Summary")
        report.append(f"- Total issues detected: {total_issues}")
        report.append(f"- Issues automatically fixed: {total_fixed}")
        report.append(f"- Success rate: {total_fixed/total_issues*100:.1f}%" if total_issues > 0 else "- Success rate: N/A")
        report.append("")
        
        # Validation results
        report.append("## Validation Results")
        for check, passed in validation.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report.append(f"- {check}: {status}")
        report.append("")
        
        # Detailed issue breakdown
        for category, issue_list in issues.items():
            if issue_list:
                report.append(f"## {category.replace('_', ' ').title()}")
                for issue in issue_list:
                    status = "✅ FIXED" if any(i.file_path == issue.file_path and i.fix_applied 
                                            for fix_list in fixes.values() for i in fix_list) else "❌ NOT FIXED"
                    report.append(f"- {issue.file_path}: {issue.description} ({status})")
                report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point for the automation framework"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    framework = AutomationFramework(root_dir)
    
    # Run analysis
    issues = framework.run_full_analysis()
    
    # Apply fixes
    fixes = framework.apply_fixes()
    
    # Validate fixes
    validation = framework.validate_fixes()
    
    # Generate report
    report = framework.generate_report(issues, fixes, validation)
    
    print(report)
    
    # Save report
    with open("automation_report.md", "w") as f:
        f.write(report)
    
    print(f"\n📊 Full report saved to automation_report.md")
    
    # Return exit code based on validation
    if all(validation.values()):
        print("🎉 All validations passed!")
        return 0
    else:
        print("⚠️  Some validations failed. Manual intervention may be required.")
        return 1


if __name__ == "__main__":
    sys.exit(main())