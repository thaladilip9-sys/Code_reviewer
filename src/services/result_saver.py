import os
import json
from datetime import datetime
from typing import Dict, List, Any

class ResultSaver:
    """Save code review results as markdown files with original folder structure"""
    
    def __init__(self, output_base_dir: str = "code_review_reports"):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)
    
    def create_folder_structure(self, original_paths: List[str], results: Dict) -> str:
        """Create folder structure mirroring the original input paths"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self.output_base_dir, f"review_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # Save summary report
        self.save_summary_report(report_dir, results, original_paths)
        
        # Save individual file reports
        self.save_individual_reports(report_dir, results)
        
        # Save original folder structure info
        self.save_structure_info(report_dir, original_paths)
        
        return report_dir
    
    def save_summary_report(self, report_dir: str, results: Dict, original_paths: List[str]) -> str:
        """Create a comprehensive summary markdown report"""
        summary_path = os.path.join(report_dir, "SUMMARY.md")
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("# Code Review Summary Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Original paths section
            f.write("## 📁 Analyzed Paths\n\n")
            for path in original_paths:
                f.write(f"- `{path}`\n")
            f.write("\n")
            
            # Overall statistics
            total_files = len(results.get('files', []))
            files_with_issues = 0
            total_issues = 0
            
            f.write("## 📊 Overall Statistics\n\n")
            f.write(f"- **Total Files Analyzed:** {total_files}\n")
            
            if results.get('standards_result'):
                standards_files = results['standards_result'].get('files', [])
                for file_result in standards_files:
                    file_has_issues = False
                    for analysis in file_result.get('analysis', []):
                        result_text = analysis.get('result', '')
                        if result_text and "No issues" not in result_text and "No output" not in result_text:
                            file_has_issues = True
                            total_issues += 1
                    if file_has_issues:
                        files_with_issues += 1
                
                f.write(f"- **Files with Issues:** {files_with_issues}\n")
                f.write(f"- **Total Issues Found:** {total_issues}\n")
            
            f.write(f"- **Overall Score:** {results.get('score', 'N/A')}\n\n")
            
            # Quick overview by file
            f.write("## 📋 Files Overview\n\n")
            f.write("| File | Language | Status | Issues |\n")
            f.write("|------|----------|--------|--------|\n")
            
            if results.get('standards_result'):
                for file_result in results['standards_result'].get('files', []):
                    filename = file_result.get('file_name', 'unknown')
                    language = file_result.get('language', 'unknown')
                    issue_count = 0
                    
                    for analysis in file_result.get('analysis', []):
                        result_text = str(analysis.get('result', ''))
                        if result_text and "No issues" not in result_text and "No output" not in result_text:
                            issue_count += 1
                    
                    status = "❌ Issues" if issue_count > 0 else "✅ Clean"
                    f.write(f"| `{filename}` | {language} | {status} | {issue_count} |\n")
            
            # Recommendations
            if results.get('recommendations'):
                f.write("\n## 💡 Recommendations\n\n")
                for rec in results['recommendations']:
                    f.write(f"- {rec}\n")
            
            # Error section
            if results.get('error'):
                f.write("\n## ❌ Errors\n\n")
                f.write(f"{results['error']}\n")
        
        return summary_path
    
    def save_individual_reports(self, report_dir: str, results: Dict) -> str:
        """Save detailed individual reports for each file"""
        individual_dir = os.path.join(report_dir, "individual_reports")
        os.makedirs(individual_dir, exist_ok=True)
        
        if not results.get('standards_result'):
            return individual_dir
        
        for file_result in results['standards_result'].get('files', []):
            filename = file_result.get('file_name', 'unknown')
            # Create safe filename for markdown
            safe_filename = filename.replace('/', '_').replace('\\', '_')
            report_path = os.path.join(individual_dir, f"{safe_filename}.md")
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# Code Review: `{filename}`\n\n")
                f.write(f"**Language:** {file_result.get('language', 'unknown')}\n\n")
                
                has_issues = False
                
                for analysis in file_result.get('analysis', []):
                    tool = analysis.get('tool', 'Unknown')
                    result = analysis.get('result', '')
                    
                    if result and "No issues" not in str(result) and "No output" not in str(result):
                        has_issues = True
                        f.write(f"## 🔧 {tool}\n\n")
                        f.write("```\n")
                        f.write(str(result))
                        f.write("\n```\n\n")
                
                if not has_issues:
                    f.write("## ✅ No Issues Found\n\n")
                    f.write("All code quality checks passed successfully.\n")
        
        return individual_dir
    
    def save_structure_info(self, report_dir: str, original_paths: List[str]) -> str:
        """Save information about the original folder structure"""
        structure_path = os.path.join(report_dir, "folder_structure.md")
        
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write("# Original Folder Structure\n\n")
            
            for path in original_paths:
                f.write(f"## Path: `{path}`\n\n")
                
                if os.path.isfile(path):
                    f.write("**Type:** File\n")
                    f.write(f"**Size:** {os.path.getsize(path)} bytes\n")
                elif os.path.isdir(path):
                    f.write("**Type:** Directory\n")
                    f.write("**Contents:**\n")
                    
                    for root, dirs, files in os.walk(path):
                        level = root.replace(path, '').count(os.sep)
                        indent = '  ' * level
                        f.write(f"{indent}- `{os.path.basename(root)}/`\n")
                        
                        sub_indent = '  ' * (level + 1)
                        for file in files[:10]:  # Limit to first 10 files per directory
                            f.write(f"{sub_indent}- `{file}`\n")
                        
                        if len(files) > 10:
                            f.write(f"{sub_indent}- ... and {len(files) - 10} more files\n")
                        break  # Only show first level for brevity
                f.write("\n")
        
        return structure_path