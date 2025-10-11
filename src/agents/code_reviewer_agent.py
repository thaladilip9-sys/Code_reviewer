from langgraph.graph import StateGraph, END
from typing import Dict, Any, List
from src.toolkit.langchain_toolkits import standards_tool
from src.services.file_reader_service import FileReader
from src.services.result_saver import ResultSaver
import os

class CodeReviewState(Dict):
    code: str = None
    files: List[Dict] = None
    file_paths: List[str] = None
    standards_result: Dict = None
    error: str = None
    report_path: str = None

class CodeReviewerAgent:
    def __init__(self, output_dir: str = "code_review_reports"):
        self.file_reader = FileReader()
        self.result_saver = ResultSaver(output_dir)
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build workflow with result saving"""
        workflow = StateGraph(CodeReviewState)
        
        workflow.add_node("read_files", self.read_files_node)
        workflow.add_node("standards_check", self.standards_node)
        workflow.add_node("save_results", self.save_results_node)
        
        workflow.set_entry_point("read_files")
        workflow.add_edge("read_files", "standards_check")
        workflow.add_edge("standards_check", "save_results")
        workflow.add_edge("save_results", END)
        
        return workflow.compile()
    
    async def read_files_node(self, state: CodeReviewState) -> CodeReviewState:
        """Read files from provided paths"""
        print("📁 Reading files from paths...")
        
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
        
        elif state.get("code"):
            state["files"] = [{
                "file_name": "main.py",
                "language": "python",
                "code": state["code"]
            }]
        else:
            state["error"] = "No code or file paths provided"
        
        print(f"📄 Found {len(state.get('files', []))} files to analyze")
        return state
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'javascript',
            '.cpp': 'cpp',
            '.c': 'cpp',
            '.h': 'cpp',
            '.hpp': 'cpp'
        }
        return language_map.get(extension, 'unknown')
    
    async def standards_node(self, state: CodeReviewState) -> CodeReviewState:
        """Run code standards analysis"""
        if state.get("error"):
            return state
        
        print("📏 Running standards check...")
        
        try:
            result = standards_tool.func(state)
            state["standards_result"] = result
            print("✅ Standards check completed successfully")
        except Exception as e:
            state["error"] = f"Standards check failed: {str(e)}"
            print(f"❌ Standards check error: {e}")
        
        return state
    
    async def save_results_node(self, state: CodeReviewState) -> CodeReviewState:
        """Save results as markdown files"""
        if state.get("error"):
            print("❌ Skipping result saving due to previous errors")
            return state
        
        print("💾 Saving results as markdown files...")
        
        try:
            original_paths = state.get("file_paths", [])
            if not original_paths and state.get("code"):
                original_paths = ["direct_code_input"]
            
            report_dir = self.result_saver.create_folder_structure(original_paths, state)
            state["report_path"] = report_dir
            print(f"✅ Results saved to: {report_dir}")
            
            # Print summary
            self._print_report_summary(state, report_dir)
            
        except Exception as e:
            state["error"] = f"Failed to save results: {str(e)}"
            print(f"❌ Error saving results: {e}")
        
        return state
    
    def _print_report_summary(self, state: CodeReviewState, report_dir: str):
        """Print a summary of the generated reports"""
        summary_path = os.path.join(report_dir, "SUMMARY.md")
        individual_dir = os.path.join(report_dir, "individual_reports")
        
        print(f"\n📋 Report Summary:")
        print(f"   📄 Summary: {summary_path}")
        print(f"   📁 Individual Reports: {individual_dir}/")
        print(f"   🗂️  Folder Structure: {os.path.join(report_dir, 'folder_structure.md')}")
        
        if state.get('standards_result'):
            files = state['standards_result'].get('files', [])
            issues_found = 0
            for file_result in files:
                for analysis in file_result.get('analysis', []):
                    result_text = str(analysis.get('result', ''))
                    if result_text and "No issues" not in result_text and "No output" not in result_text:
                        issues_found += 1
            
            print(f"   ⚠️  Total Issues Found: {issues_found}")
    
    # Public methods
    async def review_files(self, file_paths: List[str]) -> Dict:
        """Review files from paths and save results"""
        initial_state = CodeReviewState(file_paths=file_paths)
        final_state = await self.workflow.ainvoke(initial_state)
        return dict(final_state)
    
    async def review_directory(self, directory_path: str) -> Dict:
        """Review all supported files in a directory"""
        return await self.review_files([directory_path])