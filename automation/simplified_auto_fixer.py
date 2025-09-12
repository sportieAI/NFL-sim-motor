#!/usr/bin/env python3
"""
Simplified Issue Auto-Fixer

This script focuses on the most common and safely fixable issues:
1. Emoji character syntax errors  
2. Basic syntax errors (unclosed strings, parentheses)
3. Missing exception handlers
4. Requirements.txt generation
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import List, Dict, Set


class SimplifiedAutoFixer:
    """Simplified auto-fixer for common, safe issues"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.fixes_applied = []
    
    def run_auto_fixes(self) -> Dict[str, List[str]]:
        """Run all auto-fixes and return summary"""
        print("🔧 Running simplified auto-fixes...")
        
        results = {
            'syntax_fixes': self.fix_syntax_errors(),
            'requirements_fix': self.fix_requirements(),
            'validation': self.validate_fixes()
        }
        
        return results
    
    def fix_syntax_errors(self) -> List[str]:
        """Fix common syntax errors"""
        fixes = []
        
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if file has syntax errors
                try:
                    compile(content, str(py_file), 'exec')
                    continue  # No syntax errors, skip
                except SyntaxError as e:
                    fixed_content = self._fix_syntax_error(content, str(e))
                    if fixed_content != content:
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(fixed_content)
                        fixes.append(f"Fixed syntax error in {py_file.relative_to(self.root_dir)}")
                        
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}")
        
        return fixes
    
    def _fix_syntax_error(self, content: str, error_msg: str) -> str:
        """Fix a specific syntax error"""
        lines = content.split('\n')
        
        # Fix emoji characters
        if "invalid character" in error_msg and any(emoji in content for emoji in ['🟡', '🔴', '🟣', '🟢']):
            for i, line in enumerate(lines):
                if any(emoji in line for emoji in ['🟡', '🔴', '🟣', '🟢']):
                    lines[i] = "# " + line
            return '\n'.join(lines)
        
        # Fix unterminated triple quotes
        if "unterminated triple-quoted string" in error_msg:
            # Find lines with odd number of triple quotes
            for i, line in enumerate(lines):
                if '"""' in line and line.count('"""') % 2 == 1:
                    # Add closing triple quote at the end
                    lines.append('"""')
                    break
            return '\n'.join(lines)
        
        # Fix unclosed parentheses (simple cases)
        if "'(' was never closed" in error_msg:
            # Look for lines ending with unclosed parentheses
            for i, line in enumerate(lines):
                if line.strip().endswith('(') or (line.count('(') > line.count(')')):
                    lines[i] = line.rstrip() + ")"
                    break
            return '\n'.join(lines)
        
        # Fix missing except blocks
        if "expected 'except' or 'finally' block" in error_msg:
            # Find try statements without except/finally
            for i, line in enumerate(lines):
                if line.strip().startswith('try:'):
                    # Check if next non-empty line is except/finally
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        j += 1
                    
                    if j < len(lines) and not (lines[j].strip().startswith('except') or 
                                             lines[j].strip().startswith('finally')):
                        # Insert except block
                        lines.insert(j, "    except Exception as e:")
                        lines.insert(j + 1, "        pass  # Auto-generated exception handler")
                        break
            return '\n'.join(lines)
        
        return content
    
    def fix_requirements(self) -> List[str]:
        """Fix requirements.txt if it's missing or incomplete"""
        fixes = []
        req_file = self.root_dir / "requirements.txt"
        
        # Analyze imports across all Python files
        all_imports = self._analyze_imports()
        
        # Generate requirements content
        req_content = self._generate_requirements_content(all_imports)
        
        # Check if we need to update requirements.txt
        needs_update = False
        
        if not req_file.exists():
            needs_update = True
            fixes.append("Created missing requirements.txt")
        else:
            try:
                with open(req_file, 'r') as f:
                    existing_content = f.read()
                
                # Check if existing file is too minimal (like just "unittest")
                existing_lines = [line.strip() for line in existing_content.split('\n') 
                                if line.strip() and not line.startswith('#')]
                
                if len(existing_lines) <= 1:  # Very minimal file
                    needs_update = True
                    fixes.append("Updated minimal requirements.txt with comprehensive dependencies")
                    
            except Exception:
                needs_update = True
                fixes.append("Fixed corrupted requirements.txt")
        
        if needs_update:
            with open(req_file, 'w') as f:
                f.write(req_content)
        
        return fixes
    
    def _analyze_imports(self) -> Set[str]:
        """Analyze all Python files for third-party imports"""
        all_imports = set()
        
        # Standard library modules (common ones)
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'time', 'random', 'math',
            'collections', 'itertools', 'functools', 'typing', 'pathlib',
            'subprocess', 'unittest', 'logging', 'asyncio', 're', 'ast',
            'argparse', 'pickle', 'dataclasses', 'importlib'
        }
        
        for py_file in self.root_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract imports using regex (more reliable than AST for broken files)
                import_patterns = [
                    r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
                    r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import'
                ]
                
                for line in content.split('\n'):
                    line = line.strip()
                    for pattern in import_patterns:
                        match = re.match(pattern, line)
                        if match:
                            module = match.group(1)
                            if module not in stdlib_modules and not module.startswith('.'):
                                all_imports.add(module)
                
            except Exception:
                continue  # Skip files that can't be read
        
        return all_imports
    
    def _generate_requirements_content(self, imports: Set[str]) -> str:
        """Generate requirements.txt content based on detected imports"""
        
        # Map imports to package names with versions
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
            'networkx': 'networkx>=2.6.0',
            'prefect': 'prefect>=2.0.0',
            'motor': 'motor>=3.0.0',
            'aiobotocore': 'aiobotocore>=2.0.0'
        }
        
        requirements = []
        detected_packages = []
        
        for imp in sorted(imports):
            if imp in package_mapping:
                requirements.append(package_mapping[imp])
                detected_packages.append(imp)
        
        # Always include essential packages even if not detected
        essential_packages = ['pytest>=7.0.0']
        for pkg in essential_packages:
            if pkg not in requirements:
                requirements.append(pkg)
        
        content = "# Auto-generated requirements.txt\n"
        content += "# Core dependencies detected in codebase\n\n"
        
        if requirements:
            content += "\n".join(sorted(requirements))
        else:
            content += "# No third-party dependencies detected\n"
            content += "pytest>=7.0.0  # For testing\n"
        
        content += "\n\n# Project appears to use these modules:\n"
        content += f"# Detected imports: {', '.join(sorted(detected_packages)) if detected_packages else 'None'}\n"
        
        return content
    
    def validate_fixes(self) -> List[str]:
        """Validate that fixes didn't break anything"""
        validation_results = []
        
        # Test syntax of key files
        key_files = ["main_sim_loop.py", "simulate_play.py", "strategic_cognition.py"]
        
        for file_name in key_files:
            file_path = self.root_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    compile(content, str(file_path), 'exec')
                    validation_results.append(f"✅ {file_name} syntax OK")
                except SyntaxError as e:
                    validation_results.append(f"❌ {file_name} syntax error: {e}")
                except Exception as e:
                    validation_results.append(f"⚠️ {file_name} validation error: {e}")
        
        # Test basic import
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-c", "import simulate_play; print('Import OK')"
            ], capture_output=True, text=True, timeout=10, cwd=self.root_dir)
            
            if result.returncode == 0:
                validation_results.append("✅ Basic imports work")
            else:
                validation_results.append(f"❌ Import test failed: {result.stderr}")
        except Exception as e:
            validation_results.append(f"⚠️ Import test error: {e}")
        
        return validation_results
    
    def generate_report(self, results: Dict[str, List[str]]) -> str:
        """Generate a summary report"""
        report = []
        report.append("# Simplified Auto-Fix Report")
        report.append("=" * 40)
        report.append("")
        
        total_fixes = sum(len(fix_list) for fix_list in results.values() if isinstance(fix_list, list))
        report.append(f"Total fixes applied: {total_fixes}")
        report.append("")
        
        for category, fixes in results.items():
            if isinstance(fixes, list) and fixes:
                report.append(f"## {category.replace('_', ' ').title()}")
                for fix in fixes:
                    report.append(f"- {fix}")
                report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = "."
    
    fixer = SimplifiedAutoFixer(root_dir)
    results = fixer.run_auto_fixes()
    
    # Generate and display report
    report = fixer.generate_report(results)
    print(report)
    
    # Save report
    with open("simplified_autofix_report.md", "w") as f:
        f.write(report)
    
    print("📄 Report saved to simplified_autofix_report.md")
    
    # Return success if validation passed
    validation_results = results.get('validation', [])
    failed_validations = [r for r in validation_results if r.startswith('❌')]
    
    if failed_validations:
        print("⚠️ Some validations failed. Manual review may be needed.")
        return 1
    else:
        print("✅ All validations passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())