# code_standard_tool_fixed.py
import subprocess
import tempfile
import os
import sys
from langchain.agents import Tool
import chardet

class CodeStandardsChecker:
    """
    Multi-language code standards checker with Windows compatibility fixes.
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

    def run_command(self, command: list, cwd: str = None) -> str:
        """Run a shell command with better error handling and Windows support"""
        try:
            # Use shell=True on Windows for better command resolution
            use_shell = os.name == 'nt'
            
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=60,
                shell=use_shell,
                cwd=cwd
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
            # First, try to decode with utf-8
            code.encode('utf-8')
            encoding = 'utf-8'
        except UnicodeEncodeError:
            # If utf-8 fails, use latin-1 which handles all byte sequences
            encoding = 'latin-1'
        
        with tempfile.NamedTemporaryFile(
            mode="w", 
            suffix=suffix, 
            delete=False, 
            encoding=encoding
        ) as tmp:
            tmp.write(code)
            return tmp.name

    def analyze_single_file(self, file_info: dict) -> dict:
        """Analyze a single file with improved error handling"""
        code = file_info.get("code", "")
        file_path = file_info.get("file_name", "unknown")
        lang = file_info.get("language") or self.detect_language(code, file_path)

        report = {
            "file_name": file_path,
            "language": lang,
            "analysis": []
        }

        # Skip empty files
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
            # Create temporary file with proper encoding
            tmp_path = self.create_temp_file(code, suffix)
            temp_dir = os.path.dirname(tmp_path)

            if lang == "python":
                # Use specific file path for each tool
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
            # Clean up temporary file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass  # Ignore cleanup errors

        return report

    # Python-specific tools with improved Windows compatibility
    def run_python_ruff(self, file_path: str, cwd: str) -> str:
        """Run Ruff with explicit file path handling"""
        # Use check command instead of direct file analysis
        return self.run_command(["ruff", "check", "--quiet", file_path], cwd=cwd)

    def run_python_bandit(self, file_path: str, cwd: str) -> str:
        """Run Bandit with simplified approach"""
        try:
            # Use basic bandit command without complex options
            return self.run_command(["bandit", "-q", "-f", "txt", file_path], cwd=cwd)
        except:
            return "Bandit check skipped due to encoding issues"

    def run_python_mypy(self, file_path: str, cwd: str) -> str:
        """Run MyPy with encoding workaround"""
        try:
            # Try with ignore-errors flag for encoding issues
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
- Language-specific linting & formatting
- Static analysis and type checking
- Security issues and best practices
Supports Python, Java, JS/TS, C/C++, and multi-language (Semgrep).
Input schema: {"files": [{"file_name": str, "language": str, "code": str}]}
            """,
        )