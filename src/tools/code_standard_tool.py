# code_standard_tool.py
import subprocess
import tempfile
import os
import sys
from langchain.agents import Tool
import chardet
import json
from typing import Dict, List

class CodeStandardsChecker:
    """
    Multi-language code standards checker with enhanced Python tools and HTML reporting.
    """
    
    def __init__(self):
        self.language_map = {
            ".py": "python",
            ".java": "java", 
            ".js": "javascript",
            ".ts": "javascript",
            ".cpp": "cpp",
            ".c": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
        }

    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result.get('encoding', 'utf-8')
        except:
            return 'utf-8'

    # In code_standard_tool.py - modify the run_command method
    def run_command(self, command: list, cwd: str = None) -> str:
        """Run a shell command with better error handling and Windows support"""
        try:
            use_shell = os.name == 'nt'
            
            # Add creationflags for Windows to prevent event loop issues
            creationflags = 0
            if os.name == 'nt':
                creationflags = subprocess.CREATE_NO_WINDOW
                
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=60,
                shell=use_shell,
                cwd=cwd,
                creationflags=creationflags  # Add this line
            )
            
            output = result.stdout.strip() or result.stderr.strip()
            return output or "No issues found."
        except subprocess.TimeoutExpired:
            return "Command timed out after 60 seconds"
        except FileNotFoundError:
            return f"Tool not found: {command[0]}"
        except Exception as e:
            return f"Error running {' '.join(command)}: {str(e)}"

    def detect_language(self, code: str, file_path: str = None) -> str:
        """Detect language using file extension or code content."""
        if file_path:
            ext = os.path.splitext(file_path)[-1].lower()
            if ext in self.language_map:
                return self.language_map[ext]

        # Heuristic detection fallback
        if "import java" in code:
            return "java"
        if "def " in code and ("import" in code or "from " in code):
            return "python"
        if "function " in code or "console.log" in code or "const " in code or "let " in code:
            return "javascript"
        if "#include" in code:
            return "cpp"
        return "unknown"

    def create_temp_file(self, code: str, suffix: str) -> str:
        """Create temporary file with proper encoding handling"""
        try:
            code.encode('utf-8')
            encoding = 'utf-8'
        except UnicodeEncodeError:
            encoding = 'latin-1'
        
        with tempfile.NamedTemporaryFile(
            mode="w", 
            suffix=suffix, 
            delete=False, 
            encoding=encoding
        ) as tmp:
            tmp.write(code)
            return tmp.name

    # ENHANCED: Added Pylint and Flake8 methods
    def run_python_pylint(self, file_path: str, cwd: str) -> str:
        """Run Pylint with JSON output for better parsing"""
        try:
            result = self.run_command([
                "pylint", 
                "--output-format=json",
                "--reports=no",
                "--score=no",
                file_path
            ], cwd=cwd)
            
            # Parse JSON output for cleaner results
            if result and result.startswith('['):
                try:
                    pylint_data = json.loads(result)
                    if pylint_data:
                        issues = []
                        for issue in pylint_data:
                            issues.append(f"Line {issue['line']}: {issue['message']} ({issue['symbol']})")
                        return "\n".join(issues) if issues else "No Pylint issues found"
                except:
                    pass
            return result
        except:
            return "Pylint check failed"

    def run_python_flake8(self, file_path: str, cwd: str) -> str:
        """Run Flake8 with specific error codes"""
        try:
            return self.run_command([
                "flake8",
                "--format=default",
                "--max-line-length=88",
                file_path
            ], cwd=cwd)
        except:
            return "Flake8 check failed"

    def run_python_ruff(self, file_path: str, cwd: str) -> str:
        """Run Ruff with explicit file path handling"""
        return self.run_command(["ruff", "check", "--quiet", file_path], cwd=cwd)

    def run_python_bandit(self, file_path: str, cwd: str) -> str:
        """Run Bandit with simplified approach"""
        try:
            return self.run_command(["bandit", "-q", "-f", "txt", file_path], cwd=cwd)
        except:
            return "Bandit check skipped due to encoding issues"

    def run_python_mypy(self, file_path: str, cwd: str) -> str:
        """Run MyPy with encoding workaround"""
        try:
            return self.run_command([
                "mypy", 
                "--ignore-missing-imports",
                "--no-error-summary",
                file_path
            ], cwd=cwd)
        except:
            return "MyPy check skipped due to encoding issues"

    # Java tools
    def run_java_checkstyle(self, file_path: str, cwd: str) -> str:
        return self.run_command(["checkstyle", "-c", "/google_checks.xml", file_path], cwd=cwd)

    def run_java_pmd(self, file_path: str, cwd: str) -> str:
        return self.run_command(["pmd", "-d", file_path, "-R", "category/java/bestpractices.xml"], cwd=cwd)

    # JavaScript tools  
    def run_javascript_eslint(self, file_path: str, cwd: str) -> str:
        return self.run_command(["eslint", "--no-eslintrc", "--env", "browser,node", file_path], cwd=cwd)

    def run_javascript_prettier(self, file_path: str, cwd: str) -> str:
        return self.run_command(["prettier", "--check", file_path], cwd=cwd)

    # C++ tools
    def run_cpp_clang_tidy(self, file_path: str, cwd: str) -> str:
        return self.run_command(["clang-tidy", file_path, "--"], cwd=cwd)

    def run_cpp_cppcheck(self, file_path: str, cwd: str) -> str:
        return self.run_command(["cppcheck", "--enable=all", file_path], cwd=cwd)

    # Multi-language
    def run_semgrep(self, file_path: str, cwd: str) -> str:
        return self.run_command(["semgrep", "--quiet", "--config=auto", file_path], cwd=cwd)

    def analyze_single_file(self, file_info: dict) -> dict:
        """Analyze a single file with enhanced Python tools"""
        code = file_info.get("code", "")
        file_path = file_info.get("file_name", "unknown")
        lang = file_info.get("language") or self.detect_language(code, file_path)

        report = {
            "file_name": file_path,
            "language": lang,
            "code":code,
            "analysis": []
        }

        if not code.strip():
            report["analysis"].append({
                "tool": "General", 
                "result": "File is empty or contains only whitespace"
            })
            return report

        suffix_map = {
            "python": ".py",
            "java": ".java", 
            "javascript": ".js",
            "cpp": ".cpp",
            "unknown": ".txt",
        }
        
        suffix = suffix_map.get(lang, ".txt")
        tmp_path = None
        
        try:
            tmp_path = self.create_temp_file(code, suffix)
            temp_dir = os.path.dirname(tmp_path)

            if lang == "python":
                # ENHANCED: Added Pylint and Flake8 to Python analysis
                report["analysis"].append({
                    "tool": "Pylint", 
                    "result": self.run_python_pylint(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "Flake8", 
                    "result": self.run_python_flake8(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "Ruff", 
                    "result": self.run_python_ruff(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "Bandit", 
                    "result": self.run_python_bandit(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "MyPy", 
                    "result": self.run_python_mypy(tmp_path, temp_dir)
                })

            elif lang == "java":
                report["analysis"].append({
                    "tool": "Checkstyle", 
                    "result": self.run_java_checkstyle(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "PMD", 
                    "result": self.run_java_pmd(tmp_path, temp_dir)
                })

            elif lang == "javascript":
                report["analysis"].append({
                    "tool": "ESLint", 
                    "result": self.run_javascript_eslint(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "Prettier", 
                    "result": self.run_javascript_prettier(tmp_path, temp_dir)
                })

            elif lang == "cpp":
                report["analysis"].append({
                    "tool": "clang-tidy", 
                    "result": self.run_cpp_clang_tidy(tmp_path, temp_dir)
                })
                report["analysis"].append({
                    "tool": "cppcheck", 
                    "result": self.run_cpp_cppcheck(tmp_path, temp_dir)
                })

            else:
                report["analysis"].append({
                    "tool": "Semgrep", 
                    "result": self.run_semgrep(tmp_path, temp_dir)
                })

        except Exception as e:
            report["analysis"].append({
                "tool": "Error", 
                "result": f"Analysis failed: {str(e)}"
            })
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

        return report

    def analyze_files(self, state: dict) -> dict:
        """Analyze all files with improved error handling"""
        print("🔍 Running multi-file standards check...")
        results = []
        for file_info in state.get("files", []):
            try:
                result = self.analyze_single_file(file_info)
                results.append(result)
            except Exception as e:
                results.append({
                    "file_name": file_info.get("file_name", "unknown"),
                    "language": "unknown",
                    "analysis": [{"tool": "Error", "result": f"Analysis failed: {str(e)}"}]
                })
        
        state["files"] = results
        return state

    def get_tool(self) -> Tool:
        """Convert this class into a LangChain Tool."""
        return Tool(
            name="Code Standards Checker",
            func=self.analyze_files,
            description="""
Analyzes multiple source code files for:
- Language-specific linting & formatting (Pylint, Flake8, Ruff, ESLint, etc.)
- Static analysis and type checking (MyPy, Bandit, clang-tidy)
- Security issues and best practices
Supports Python, Java, JS/TS, C/C++, and multi-language (Semgrep).
Input schema: {"files": [{"file_name": str, "language": str, "code": str}]}
            """,
        )