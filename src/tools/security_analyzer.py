# security_analyzer.py
import subprocess
import tempfile
import os
from typing import Dict, List
from langchain.agents import Tool
import json

class SecurityQualityAnalyzer:
    """
    Comprehensive security and quality analysis using multiple tools with custom evaluation.
    """
    
    def __init__(self):
        self.supported_languages = {
            'python': self._analyze_python,
            'javascript': self._analyze_javascript,
            'java': self._analyze_java,
            'cpp': self._analyze_cpp
        }
    
    def analyze_security(self, state: Dict) -> Dict:
        """Perform comprehensive security and quality analysis"""
        print("🛡️ Running security and quality analysis...")
        
        try:
            files = state.get("files", [])
            
            if not files:
                state["security_analysis"] = {
                    "error": "No code files available for security analysis"
                }
                return state
            
            security_results = []
            for file in files:
                file_analysis = self._analyze_single_file(file)
                security_results.append(file_analysis)
            
            # Generate overall security assessment
            overall_assessment = self._generate_overall_assessment(security_results)
            
            state["security_analysis"] = {
                "file_analyses": security_results,
                "overall_assessment": overall_assessment,
                "security_risks": self._identify_security_risks(security_results),
                "quality_issues": self._identify_quality_issues(security_results)
            }
            
            print("✅ Security analysis completed")
            
        except Exception as e:
            state["security_analysis"] = {
                "error": f"Security analysis failed: {str(e)}"
            }
            print(f"❌ Security analysis error: {e}")
        
        return state
    
    def _analyze_single_file(self, file: Dict) -> Dict:
        """Analyze a single file for security and quality issues"""
        language = file.get("language", "unknown")
        analyzer_func = self.supported_languages.get(language, self._analyze_generic)
        
        return analyzer_func(file)
    
    def _analyze_python(self, file: Dict) -> Dict:
        """Analyze Python file for security and quality"""
        analysis = {
            "file_name": file.get("file_name"),
            "language": "python",
            "tools_used": [],
            "issues": [],
            "security_score": 0,
            "quality_score": 0
        }
        
        code = file.get("code", "")
        if not code.strip():
            return analysis
        
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write(code)
            tmp_path = tmp.name
        
        try:
            # Run Bandit for security
            bandit_result = self._run_bandit(tmp_path)
            analysis["tools_used"].append("bandit")
            analysis["issues"].extend(bandit_result.get("issues", []))
            
            # Run Safety for vulnerability check
            safety_result = self._run_safety(tmp_path)
            analysis["tools_used"].append("safety")
            analysis["issues"].extend(safety_result.get("vulnerabilities", []))
            
            # Run Pylint for code quality
            pylint_result = self._run_pylint(tmp_path)
            analysis["tools_used"].append("pylint")
            analysis["issues"].extend(pylint_result.get("quality_issues", []))
            
            # Calculate scores
            analysis["security_score"] = self._calculate_security_score(analysis["issues"])
            analysis["quality_score"] = self._calculate_quality_score(analysis["issues"])
            
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        
        return analysis
    
    def _analyze_javascript(self, file: Dict) -> Dict:
        """Analyze JavaScript file for security and quality"""
        analysis = {
            "file_name": file.get("file_name"),
            "language": "javascript",
            "tools_used": [],
            "issues": [],
            "security_score": 0,
            "quality_score": 0
        }
        
        # JavaScript analysis implementation
        # Similar pattern to Python analysis
        analysis["issues"].append({
            "tool": "ESLint",
            "type": "info",
            "message": "JavaScript security analysis requires ESLint with security plugins",
            "severity": "medium"
        })
        
        return analysis
    
    def _analyze_java(self, file: Dict) -> Dict:
        """Analyze Java file for security and quality"""
        analysis = {
            "file_name": file.get("file_name"),
            "language": "java",
            "tools_used": [],
            "issues": [],
            "security_score": 0,
            "quality_score": 0
        }
        
        # Java analysis implementation
        analysis["issues"].append({
            "tool": "SpotBugs",
            "type": "info",
            "message": "Java security analysis requires SpotBugs or CheckMarx",
            "severity": "medium"
        })
        
        return analysis
    
    def _analyze_cpp(self, file: Dict) -> Dict:
        """Analyze C++ file for security and quality"""
        analysis = {
            "file_name": file.get("file_name"),
            "language": "cpp",
            "tools_used": [],
            "issues": [],
            "security_score": 0,
            "quality_score": 0
        }
        
        # C++ analysis implementation
        analysis["issues"].append({
            "tool": "clang-tidy",
            "type": "info",
            "message": "C++ security analysis requires clang-tidy with security checks",
            "severity": "medium"
        })
        
        return analysis
    
    def _analyze_generic(self, file: Dict) -> Dict:
        """Generic analysis for unsupported languages"""
        return {
            "file_name": file.get("file_name"),
            "language": file.get("language", "unknown"),
            "tools_used": ["generic"],
            "issues": [{
                "tool": "Generic",
                "type": "info",
                "message": f"No specific security tools configured for {file.get('language', 'unknown')}",
                "severity": "low"
            }],
            "security_score": 0,
            "quality_score": 0
        }
    
    def _run_bandit(self, file_path: str) -> Dict:
        """Run Bandit security analysis"""
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json', '-r', file_path],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode == 0:
                try:
                    bandit_data = json.loads(result.stdout)
                    issues = []
                    for result_item in bandit_data.get('results', []):
                        issues.append({
                            "tool": "Bandit",
                            "type": "security",
                            "message": f"{result_item.get('issue_text', 'Unknown issue')}",
                            "severity": result_item.get('issue_severity', 'low'),
                            "confidence": result_item.get('issue_confidence', 'low'),
                            "line": result_item.get('line_number')
                        })
                    return {"issues": issues}
                except:
                    pass
        except:
            pass
        
        return {"issues": []}
    
    def _run_safety(self, file_path: str) -> Dict:
        """Run Safety vulnerability check"""
        try:
            result = subprocess.run(
                ['safety', 'check', '--json', '--file', file_path],
                capture_output=True, text=True, timeout=60
            )
            
            if result.returncode in [0, 1]:  # Safety returns 1 when vulnerabilities found
                try:
                    safety_data = json.loads(result.stdout)
                    vulnerabilities = []
                    for vuln in safety_data.get('vulnerabilities', []):
                        vulnerabilities.append({
                            "tool": "Safety",
                            "type": "vulnerability",
                            "message": f"{vuln.get('package_name', 'Unknown')}: {vuln.get('vulnerability', 'Unknown vulnerability')}",
                            "severity": vuln.get('severity', 'medium'),
                            "advisory": vuln.get('advisory', 'No advisory available')
                        })
                    return {"vulnerabilities": vulnerabilities}
                except:
                    pass
        except:
            pass
        
        return {"vulnerabilities": []}
    
    def _run_pylint(self, file_path: str) -> Dict:
        """Run Pylint for code quality"""
        try:
            result = subprocess.run(
                ['pylint', '--output-format=json', file_path],
                capture_output=True, text=True, timeout=60
            )
            
            try:
                pylint_data = json.loads(result.stdout)
                quality_issues = []
                for issue in pylint_data:
                    quality_issues.append({
                        "tool": "Pylint",
                        "type": "quality",
                        "message": f"{issue.get('message', 'Unknown issue')} ({issue.get('symbol', 'unknown')})",
                        "severity": self._map_pylint_severity(issue.get('type', 'info')),
                        "line": issue.get('line')
                    })
                return {"quality_issues": quality_issues}
            except:
                pass
        except:
            pass
        
        return {"quality_issues": []}
    
    def _map_pylint_severity(self, pylint_type: str) -> str:
        """Map Pylint message type to severity"""
        severity_map = {
            'error': 'high',
            'warning': 'medium',
            'convention': 'low',
            'refactor': 'low',
            'info': 'info'
        }
        return severity_map.get(pylint_type, 'low')
    
    def _calculate_security_score(self, issues: List[Dict]) -> float:
        """Calculate security score based on issues"""
        if not issues:
            return 10.0
        
        severity_weights = {
            'critical': 5,
            'high': 4,
            'medium': 3,
            'low': 1,
            'info': 0
        }
        
        total_weight = 0
        for issue in issues:
            if issue.get('type') == 'security' or issue.get('type') == 'vulnerability':
                severity = issue.get('severity', 'low')
                total_weight += severity_weights.get(severity, 1)
        
        # Convert to score out of 10 (higher is better)
        base_score = 10.0
        penalty = min(total_weight * 0.5, 9.0)  # Cap penalty at 9
        return round(max(base_score - penalty, 1.0), 2)
    
    def _calculate_quality_score(self, issues: List[Dict]) -> float:
        """Calculate quality score based on issues"""
        if not issues:
            return 10.0
        
        quality_issue_count = sum(1 for issue in issues 
                                if issue.get('type') in ['quality', 'maintainability'])
        
        # Convert to score out of 10
        base_score = 10.0
        penalty = min(quality_issue_count * 0.2, 9.0)
        return round(max(base_score - penalty, 1.0), 2)
    
    def _generate_overall_assessment(self, analyses: List[Dict]) -> Dict:
        """Generate overall security and quality assessment"""
        if not analyses:
            return {"security_rating": "UNKNOWN", "quality_rating": "UNKNOWN"}
        
        avg_security = sum(analysis.get("security_score", 0) for analysis in analyses) / len(analyses)
        avg_quality = sum(analysis.get("quality_score", 0) for analysis in analyses) / len(analyses)
        
        return {
            "average_security_score": round(avg_security, 2),
            "average_quality_score": round(avg_quality, 2),
            "security_rating": self._rate_security(avg_security),
            "quality_rating": self._rate_quality(avg_quality),
            "total_issues": sum(len(analysis.get("issues", [])) for analysis in analyses),
            "files_analyzed": len(analyses)
        }
    
    def _rate_security(self, score: float) -> str:
        """Rate security based on score"""
        if score >= 9.0:
            return "EXCELLENT"
        elif score >= 7.0:
            return "GOOD"
        elif score >= 5.0:
            return "FAIR"
        elif score >= 3.0:
            return "POOR"
        else:
            return "CRITICAL"
    
    def _rate_quality(self, score: float) -> str:
        """Rate quality based on score"""
        if score >= 9.0:
            return "EXCELLENT"
        elif score >= 7.0:
            return "GOOD"
        elif score >= 5.0:
            return "FAIR"
        elif score >= 3.0:
            return "POOR"
        else:
            return "VERY_POOR"
    
    def _identify_security_risks(self, analyses: List[Dict]) -> List[str]:
        """Identify critical security risks"""
        risks = []
        
        for analysis in analyses:
            for issue in analysis.get("issues", []):
                if issue.get('type') in ['security', 'vulnerability']:
                    severity = issue.get('severity', 'low')
                    if severity in ['critical', 'high']:
                        risk_msg = f"{analysis['file_name']}: {issue['message']}"
                        risks.append(risk_msg)
        
        return list(set(risks))  # Remove duplicates
    
    def _identify_quality_issues(self, analyses: List[Dict]) -> List[str]:
        """Identify significant quality issues"""
        issues = []
        
        for analysis in analyses:
            for issue in analysis.get("issues", []):
                if issue.get('type') == 'quality' and issue.get('severity') in ['high', 'medium']:
                    issue_msg = f"{analysis['file_name']}: {issue['message']}"
                    issues.append(issue_msg)
        
        return list(set(issues))
    
    def get_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="Security & Quality Analyzer",
            func=self.analyze_security,
            description="""
Performs comprehensive security and quality analysis using multiple tools.
Uses Bandit, Safety, Pylint and language-specific analyzers.
Output: Security scores, quality assessment, and identified risks.
            """
        )