# code_reviewer_agent.py
from langgraph.graph import StateGraph, END
from typing import Dict, Any, List, Optional
from src.tools.code_standard_tool import CodeStandardsChecker
from src.tools.requirement_validator_tool import RequirementValidator
from src.tools.deep_evaluator_tool import DeepEvaluator
from src.tools.security_analyzer import SecurityQualityAnalyzer
from src.tools.consolidated_reporter_tool import ConsolidatedReporter
from src.services.file_reader_service import FileReader
import os
import asyncio,datetime

class CodeReviewState(Dict):
    # Input fields
    code: Optional[str] = None
    files: Optional[List[Dict]] = None
    file_paths: Optional[List[str]] = None
    requirements: Optional[Dict] = None
    
    # Analysis results
    standards_result: Optional[Dict] = None
    requirement_validation: Optional[Dict] = None
    deep_evaluation: Optional[Dict] = None
    security_analysis: Optional[Dict] = None
    consolidated_report: Optional[Dict] = None
    
    # Output paths
    html_report_path: Optional[str] = None
    report_directory: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    current_step: Optional[str] = None

class CodeReviewerAgent:
    """
    Main agent orchestrating the complete code review workflow.
    """
    
    def __init__(self, output_dir: str = "code_review_reports"):
        self.file_reader = FileReader()
        self.output_dir = output_dir
        
        # Initialize all tools
        self.standards_checker = CodeStandardsChecker()
        self.requirement_validator = RequirementValidator()
        self.deep_evaluator = DeepEvaluator()
        self.security_analyzer = SecurityQualityAnalyzer()
        self.consolidated_reporter = ConsolidatedReporter(output_dir)
        
        # Build workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build comprehensive code review workflow"""
        workflow = StateGraph(CodeReviewState)
        
        # Add all nodes
        workflow.add_node("read_files", self.read_files_node)
        workflow.add_node("standards_check", self.standards_check_node)
        workflow.add_node("requirement_validation", self.requirement_validation_node)
        # workflow.add_node("deep_evaluation", self.deep_evaluation_node)
        workflow.add_node("generate_reports", self.generate_reports_node)
        
        # Define workflow
        workflow.set_entry_point("read_files")
        
        # Main sequential flow
        workflow.add_edge("read_files", "standards_check")
        workflow.add_edge("standards_check", "requirement_validation")
        workflow.add_edge("requirement_validation", "generate_reports")
        workflow.add_edge("generate_reports", END)
        
        return workflow.compile()
    
    async def read_files_node(self, state: CodeReviewState) -> CodeReviewState:
        """Read files from provided paths or direct code"""
        state["current_step"] = "read_files"
        print("📁 Reading files from paths...")
        
        try:
            if state.get("file_paths"):
                files_info = self.file_reader.read_files_from_paths(state["file_paths"])
                
                valid_files = []
                for file_info in files_info:
                    if "error" not in file_info:
                        valid_files.append({
                            "file_name": file_info["file_name"],
                            "language": self._detect_language_from_extension(file_info["extension"]),
                            "code": file_info["code"]
                        })
                    else:
                        print(f"⚠️ Skipping {file_info['file_name']}: {file_info['error']}")
                
                state["files"] = valid_files
                
                if not valid_files:
                    state["error"] = "No valid files found to analyze"
                    return state
            
            elif state.get("code"):
                state["files"] = [{
                    "file_name": "main.py",
                    "language": "python",
                    "code": state["code"]
                }]
            else:
                state["error"] = "No code or file paths provided"
                return state
            
            print(f"📄 Found {len(state.get('files', []))} files to analyze")
            
        except Exception as e:
            state["error"] = f"Error reading files: {str(e)}"
            print(f"❌ File reading error: {e}")
        
        return state
    
    async def standards_check_node(self, state: CodeReviewState) -> CodeReviewState:
        """Run code standards analysis"""
        if state.get("error"):
            return state
        
        state["current_step"] = "standards_check"
        print("📏 Running code standards analysis...")
        
        try:
            standards_tool = self.standards_checker.get_tool()
            result = standards_tool.func(state)
            state["standards_result"] = result
            
            
            # Calculate standards summary
            standards_summary = self._calculate_standards_summary(result)
            print(f"✅ Standards analysis completed: {standards_summary}")
            
        except Exception as e:
            state["error"] = f"Standards analysis failed: {str(e)}"
            print(f"❌ Standards analysis error: {e}")
        
        return state
    
    async def requirement_validation_node(self, state: CodeReviewState) -> CodeReviewState:
        """Validate requirements implementation"""
        if state.get("error"):
            return state
        
        state["current_step"] = "requirement_validation"

        # import json
        # with open("state.json",'w') as f:
        #     json.dump(state,f,indent=4)
        
        # Skip if no requirements provided
        if not state.get("requirements"):
            print("ℹ️ No requirements provided, skipping requirement validation")
            state["requirement_validation"] = {
                "skipped": True,
                "reason": "No requirements provided for validation"
            }
            return state
        
        print("🔍 Validating requirements implementation...")
        
        try:
            requirement_tool = self.requirement_validator.get_tool()
            result = requirement_tool.func(state)

            # import json
            # with open("result.json",'w') as f:
            #     json.dump(result,f,indent=4)

        
            # print("requirement_validation", state)
            
            if "error" not in result:
                coverage_score = result.get("alignment_analysis", {}).get("overall_alignment_score", 0)
                print(f"✅ Requirement validation completed: Score {coverage_score:.2f}")
            else:
                print(f"⚠️ Requirement validation completed with issues")
            
        except Exception as e:
            state["error"] = f"Requirement validation failed: {str(e)}"
            print(f"❌ Requirement validation error: {e}")
        
        return state
    
    async def deep_evaluation_node(self, state: CodeReviewState) -> CodeReviewState:
        """Perform deep evaluation using custom metrics"""
        if state.get("error"):
            return state
        
        state["current_step"] = "deep_evaluation"
        print("🔬 Running deep evaluation with custom metrics...")
        
        try:
            # Run the deep evaluation in a thread pool to avoid blocking
            import asyncio
            loop = asyncio.get_event_loop()
            deep_eval_tool = self.deep_evaluator.get_tool()
            await asyncio.sleep(0.01)
            
            # Run the synchronous function in a thread pool
            result = await loop.run_in_executor(None, deep_eval_tool.func, state)
            state["deep_evaluation"] = result
            
            if "error" not in result:
                overall_score = result.get("overall_score", 0)
                summary = result.get("summary", "No summary available")
                print(f"✅ Deep evaluation completed: Overall score {overall_score}/1.0")
                if summary:
                    first_line = summary.splitlines()[0] if summary else 'No summary'
                    print(f"   Summary: {first_line}")
            else:
                print(f"⚠️ Deep evaluation completed with issues")
            
        except Exception as e:
            state["error"] = f"Deep evaluation failed: {str(e)}"
            print(f"❌ Deep evaluation error: {e}")
        
        return state    
    async def security_analysis_node(self, state: CodeReviewState) -> CodeReviewState:
        """Perform security and quality analysis"""
        if state.get("error"):
            return state
        
        state["current_step"] = "security_analysis"
        print("🛡️ Running security and quality analysis...")
        
        try:
            security_tool = self.security_analyzer.get_tool()
            result = security_tool.func(state)
            state["security_analysis"] = result
            
            if "error" not in result:
                overall = result.get("overall_assessment", {})
                security_score = overall.get("average_security_score", 0)
                security_rating = overall.get("security_rating", "UNKNOWN")
                print(f"✅ Security analysis completed: {security_rating} ({security_score}/10)")
            else:
                print(f"⚠️ Security analysis completed with issues")
            
        except Exception as e:
            state["error"] = f"Security analysis failed: {str(e)}"
            print(f"❌ Security analysis error: {e}")
        
        return state
    
    async def generate_reports_node(self, state: CodeReviewState) -> CodeReviewState:
        """Generate consolidated reports"""
        if state.get("error"):
            print("❌ Skipping report generation due to previous errors")
            return state
                
        state["current_step"] = "generate_reports"
        print("📋 Generating consolidated reports...")
        
        try:
            reporter_tool = self.consolidated_reporter.get_tool()
            result = reporter_tool.func(state)
            state["consolidated_report"] = result
            
            if "error" not in result:
                html_path = result.get("html_report_path")
                report_dir = result.get("report_directory")
                
                if html_path and os.path.exists(html_path):
                    print(f"✅ Consolidated reports generated successfully!")
                    print(f"   🌐 HTML Report: file://{os.path.abspath(html_path)}")
                    print(f"   📁 Location: {report_dir}")
                    
                    # Print final summary
                    self._print_final_summary(state)
                else:
                    state["error"] = "Report files were not created properly"
            else:
                state["error"] = result.get("error", "Unknown report generation error")
            
        except Exception as e:
            state["error"] = f"Report generation failed: {str(e)}"
            print(f"❌ Report generation error: {e}")
        
        return state
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala'
        }
        return language_map.get(extension.lower(), 'unknown')
    
    def _calculate_standards_summary(self, standards_result: Dict) -> str:
        """Calculate summary for standards analysis"""
        if not standards_result or "files" not in standards_result:
            return "No standards data"
        
        files = standards_result["files"]
        total_issues = 0
        analyzed_files = 0
        
        for file_data in files:
            for analysis in file_data.get("analysis", []):
                result = analysis.get("result", "")
                if result and "No issues" not in result and "No output" not in result:
                    total_issues += 1
            analyzed_files += 1
        
        return f"{analyzed_files} files, {total_issues} issues"
    
    def _print_final_summary(self, state: CodeReviewState):
        """Print comprehensive final summary"""
        print("\n" + "="*60)
        print("🎉 CODE REVIEW COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Standards summary
        if state.get("standards_result"):
            standards_summary = self._calculate_standards_summary(state["standards_result"])
            print(f"📏 Standards: {standards_summary}")
        
        # Requirements summary
        if state.get("requirement_validation") and "skipped" not in state["requirement_validation"]:
            req_data = state["requirement_validation"]
            if "error" not in req_data:
                coverage_score = req_data.get("alignment_analysis", {}).get("overall_alignment_score", 0)
                print(f"🔍 Requirements: {coverage_score:.1%} alignment")
        
        # Deep evaluation summary
        if state.get("deep_evaluation") and "error" not in state["deep_evaluation"]:
            deep_eval_data = state["deep_evaluation"]
            overall_score = deep_eval_data.get("overall_scores", {}).get("overall_score", 0)
            print(f"🔬 Deep Evaluation: {overall_score}/5.0 overall")
        
        # Security summary
        if state.get("security_analysis") and "error" not in state["security_analysis"]:
            security_data = state["security_analysis"]
            overall = security_data.get("overall_assessment", {})
            security_score = overall.get("average_security_score", 0)
            security_rating = overall.get("security_rating", "UNKNOWN")
            print(f"🛡️ Security: {security_rating} ({security_score}/10)")
        
        # Report locations
        if state.get("consolidated_report"):
            report_data = state["consolidated_report"]
            html_path = report_data.get("html_report_path")
            if html_path:
                print(f"\n📊 Reports Generated:")
                print(f"   🌐 Main Report: file://{os.path.abspath(html_path)}")
                print(f"   📁 Directory: {report_data.get('report_directory')}")
        
        print("="*60)
    
    # Public API methods
    async def review_files(self, file_paths: List[str], requirements: Optional[Dict] = None) -> Dict:
        """
        Review files from paths with optional requirements.
        
        Args:
            file_paths: List of file paths to analyze
            requirements: Optional requirements dict for validation
            
        Returns:
            Complete analysis results
        """
        initial_state = CodeReviewState(
            file_paths=file_paths,
            requirements=requirements
        )
        
        print(f"🚀 Starting code review for {len(file_paths)} files... {file_paths}")
        final_state = await self.workflow.ainvoke(initial_state)
        return dict(final_state)
    
    async def review_directory(self, directory_path: str, requirements: Optional[Dict] = None) -> Dict:
        """
        Review all supported files in a directory.
        
        Args:
            directory_path: Path to directory containing code files
            requirements: Optional requirements dict for validation
            
        Returns:
            Complete analysis results
        """
        return await self.review_files([directory_path], requirements)
    
    async def review_code(self, code: str, file_name: str = "main.py", 
                         requirements: Optional[Dict] = None) -> Dict:
        """
        Review direct code input.
        
        Args:
            code: Source code string
            file_name: Name for the code file
            requirements: Optional requirements dict for validation
            
        Returns:
            Complete analysis results
        """
        initial_state = CodeReviewState(
            code=code,
            requirements=requirements
        )
        
        print(f"🚀 Starting code review for direct code input...")
        final_state = await self.workflow.ainvoke(initial_state)
        return dict(final_state)
    
    async def review_with_custom_requirements(self, file_paths: List[str], 
                                            user_stories: List[str],
                                            acceptance_criteria: List[str]) -> Dict:
        """
        Review files with structured requirements from user stories.
        
        Args:
            file_paths: List of file paths to analyze
            user_stories: List of user story descriptions
            acceptance_criteria: List of acceptance criteria
            
        Returns:
            Complete analysis results
        """
        requirements = {
            "user_stories": user_stories,
            "acceptance_criteria": acceptance_criteria,
            "timestamp": str(datetime.now())
        }
        
        return await self.review_files(file_paths, requirements)

# Utility function for easy usage
async def create_code_review_agent(output_dir: str = "code_review_reports") -> CodeReviewerAgent:
    """
    Factory function to create and return a CodeReviewerAgent instance.
    
    Args:
        output_dir: Directory for storing reports
        
    Returns:
        Configured CodeReviewerAgent instance
    """
    return CodeReviewerAgent(output_dir)

