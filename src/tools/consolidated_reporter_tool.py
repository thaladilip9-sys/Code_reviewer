# consolidated_reporter.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any
from langchain.agents import Tool

class ConsolidatedReporter:
    """
    Generates comprehensive HTML reports from all analysis tools.
    Includes expandable sections with detailed analysis results and YAML specification analysis.
    """
    
    def __init__(self, output_dir: str = "code_review_reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_consolidated_report(self, state: Dict) -> Dict:
        """Generate comprehensive HTML report from all analyses"""
        print("📋 Generating comprehensive HTML report...")
        
        try:
            # Create report directory
            report_dir = os.path.join(self.output_dir, f"full_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(report_dir, exist_ok=True)

            # Extract and validate all analysis data
            analysis_data = self._extract_analysis_data(state)
            
            # Generate comprehensive HTML report
            html_content = self._create_comprehensive_html(analysis_data)
            html_file = os.path.join(report_dir, "comprehensive_code_review.html")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate JSON summary
            json_summary = self._generate_detailed_json_summary(analysis_data)
            json_file = os.path.join(report_dir, "detailed_analysis.json")
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_summary, f, indent=2, ensure_ascii=False)
            
            # Return only paths, not the entire state
            result_state = {
                "html_report_path": html_file,
                "report_directory": report_dir,
                "json_summary_path": json_file
            }
            
            print(f"✅ Comprehensive HTML report generated: {html_file}")
            return result_state
            
        except Exception as e:
            error_state = {"error": f"Report generation failed: {str(e)}"}
            print(f"❌ Report generation error: {e}")
            return error_state
    
    def _extract_analysis_data(self, state: Dict) -> Dict:
        """Extract analysis data from state"""
        analysis_data = {
            "standards": self._extract_standards_data(state.get("standards_result")),
            "requirements": self._extract_requirements_data(state.get("requirement_validation")),
            "deep_eval": self._extract_deep_eval_data(state.get("deep_evaluation")),
            "yaml_spec": self._extract_yaml_spec_data(state.get("yaml_spec_data")),
            "original_requirements": state.get("requirements", {}),
            "files_analyzed": len(state.get("files", [])),
            "error": state.get("error")
        }
        return analysis_data
    
    def _extract_yaml_spec_data(self, yaml_spec_data: Any) -> Dict:
        """Extract YAML specification analysis data"""
        if not yaml_spec_data:
            return {"available": False}
        
        if "error" in yaml_spec_data:
            return {"available": False, "error": yaml_spec_data["error"]}
        
        return {
            "available": True,
            "specification_used": yaml_spec_data.get("specification_used", {}),
            "validation_steps": yaml_spec_data.get("validation_steps", {}),
            "overall_metrics": yaml_spec_data.get("overall_metrics", {})
        }
    
    def _extract_standards_data(self, standards_data: Any) -> Dict:
        """Extract standards analysis data"""
        if not standards_data or "files" not in standards_data:
            return {"available": False, "files": []}
        
        files = []
        total_issues = 0
        
        for file_data in standards_data.get("files", []):
            if isinstance(file_data, dict):
                file_name = file_data.get("file_name", "Unknown")
                language = file_data.get("language", "unknown")
                analyses = file_data.get("analysis", [])
                
                # Count issues and extract tool results
                file_issues = 0
                tool_results = []
                
                for analysis in analyses:
                    if isinstance(analysis, dict):
                        tool = analysis.get("tool", "Unknown")
                        result = analysis.get("result", "")
                        
                        # Count issues based on result content
                        if result and "No issues" not in result and "No output" not in result:
                            file_issues += 1
                        
                        tool_results.append({
                            "tool": tool,
                            "result": result
                        })
                
                total_issues += file_issues
                
                files.append({
                    "file_name": file_name,
                    "language": language,
                    "issue_count": file_issues,
                    "tool_results": tool_results
                })
        
        return {
            "available": True,
            "files": files,
            "total_issues": total_issues
        }
    
    def _extract_requirements_data(self, requirement_data: Any) -> Dict:
        """Extract requirements validation data - UPDATED for new structure"""
        if not requirement_data:
            return {"available": False, "skipped": True}
        
        if "error" in requirement_data:
            return {"available": False, "error": requirement_data["error"]}
        
        if "skipped" in requirement_data:
            return {"available": False, "skipped": True}
        
        # Extract data from the new standardized structure
        comprehensive_analysis = requirement_data.get("comprehensive_analysis", {})
        alignment_scores = comprehensive_analysis.get("overall_alignment_scores", {})
        alignment_analysis = requirement_data.get("alignment_analysis", {})
        
        # Calculate overall metrics from the new structure
        user_stories = alignment_scores.get("user_stories", {})
        functional_reqs = alignment_scores.get("functional_requirements", {})
        security_reqs = alignment_scores.get("security_requirements", {})
        non_functional_reqs = alignment_scores.get("non_functional_requirements", {})
        
        # Calculate totals
        total_requirements = (
            user_stories.get("total", 0) + 
            functional_reqs.get("total", 0) + 
            security_reqs.get("total", 0) +
            non_functional_reqs.get("total", 0)
        )
        
        total_implemented = (
            user_stories.get("implemented", 0) + 
            functional_reqs.get("implemented", 0) + 
            security_reqs.get("implemented", 0) +
            non_functional_reqs.get("implemented", 0)
        )
        
        # Calculate overall alignment score (weighted average)
        if total_requirements > 0:
            user_stories_weight = user_stories.get("total", 0) / total_requirements
            functional_weight = functional_reqs.get("total", 0) / total_requirements
            security_weight = security_reqs.get("total", 0) / total_requirements
            non_functional_weight = non_functional_reqs.get("total", 0) / total_requirements
            
            overall_score = (
                user_stories.get("average_confidence_score", 0) * user_stories_weight +
                functional_reqs.get("average_confidence_score", 0) * functional_weight +
                security_reqs.get("average_confidence_score", 0) * security_weight +
                non_functional_reqs.get("average_confidence_score", 0) * non_functional_weight
            )
        else:
            overall_score = 0
        
        return {
            "available": True,
            "comprehensive_analysis": comprehensive_analysis,
            "alignment_scores": alignment_scores,
            "alignment_analysis": alignment_analysis,
            "overall_score": overall_score,
            "total_requirements": total_requirements,
            "total_implemented": total_implemented,
            "coverage_percentage": (total_implemented / total_requirements * 100) if total_requirements > 0 else 0
        }
    
    def _extract_deep_eval_data(self, deep_eval_data: Any) -> Dict:
        """Extract deep evaluation data"""
        if not deep_eval_data:
            return {"available": False}
        
        if "error" in deep_eval_data:
            return {"available": False, "error": deep_eval_data["error"]}
        
        overall_scores = deep_eval_data.get("overall_scores", {})
        file_evaluations = deep_eval_data.get("file_evaluations", [])
        
        return {
            "available": True,
            "overall_score": overall_scores.get("overall_score", 0),
            "file_evaluations": file_evaluations,
            "summary": deep_eval_data.get("summary", ""),
            "recommendations": deep_eval_data.get("recommendations", [])
        }
    
    def _create_comprehensive_html(self, analysis_data: Dict) -> str:
        """Create comprehensive HTML report with all analysis results"""
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(analysis_data)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Code Review Report</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --primary: #2563eb;
            --secondary: #1e40af;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --info: #3b82f6;
            --background: #f8fafc;
            --surface: #ffffff;
            --text: #1f2937;
            --border: #e5e7eb;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--background);
            padding: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: var(--surface);
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
            font-weight: 300;
        }}
        
        /* Executive Summary */
        .executive-summary {{
            padding: 2rem;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--surface);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border);
            transition: transform 0.2s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            color: #6b7280;
            font-weight: 500;
            font-size: 0.9rem;
        }}
        
        .metric-subtext {{
            font-size: 0.8rem;
            color: #9ca3af;
            margin-top: 0.25rem;
        }}
        
        .score-excellent {{ color: var(--success); }}
        .score-good {{ color: var(--primary); }}
        .score-fair {{ color: var(--warning); }}
        .score-poor {{ color: var(--error); }}
        
        /* Sections */
        .section {{
            padding: 2rem;
            border-bottom: 1px solid var(--border);
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .section-title i {{
            font-size: 1.25rem;
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .status-success {{ background: var(--success); color: white; }}
        .status-warning {{ background: var(--warning); color: white; }}
        .status-error {{ background: var(--error); color: white; }}
        .status-info {{ background: var(--info); color: white; }}
        
        /* Expandable Sections */
        .expandable-section {{
            margin-top: 1.5rem;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .expandable-header {{
            background: #f8fafc;
            padding: 1rem 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background-color 0.2s;
        }}
        
        .expandable-header:hover {{
            background: #f1f5f9;
        }}
        
        .expandable-title {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }}
        
        .expandable-icon {{
            transition: transform 0.3s ease;
        }}
        
        .expandable-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            background: white;
        }}
        
        .expandable-content.expanded {{
            max-height: 1000px;
            overflow-y: auto;
        }}
        
        .tool-results {{
            padding: 1.5rem;
            background: white;
        }}
        
        .tool-result {{
            margin-bottom: 1.5rem;
            padding: 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            background: #f8fafc;
        }}
        
        .tool-name {{
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 0.5rem;
        }}
        
        .tool-output {{
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            overflow-x: auto;
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .requirement-item {{
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            border-left: 4px solid var(--success);
            background: #f0fdf4;
        }}
        
        .requirement-missing {{
            border-left-color: var(--error);
            background: #fef2f2;
        }}
        
        .requirement-partial {{
            border-left-color: var(--warning);
            background: #fffbeb;
        }}
        
        .file-list {{
            margin: 1.5rem 0;
        }}
        
        .file-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            margin-bottom: 0.5rem;
            background: var(--surface);
        }}
        
        .file-name {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 500;
        }}
        
        /* YAML Spec Styles */
        .violation-item {{
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            border-left: 4px solid var(--error);
            background: #fef2f2;
        }}
        
        .violation-warning {{
            border-left-color: var(--warning);
            background: #fffbeb;
        }}
        
        .violation-info {{
            border-left-color: var(--info);
            background: #f0f9ff;
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        
        .severity-critical {{ background: #dc2626; color: white; }}
        .severity-high {{ background: #ef4444; color: white; }}
        .severity-medium {{ background: #f59e0b; color: white; }}
        .severity-low {{ background: #3b82f6; color: white; }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #9ca3af;
            font-size: 0.9rem;
            border-top: 1px solid var(--border);
            background: var(--background);
        }}
        
        @media (max-width: 768px) {{
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1><i class="fas fa-code"></i> Comprehensive Code Review Report</h1>
            <div class="subtitle">AI-Powered Code Quality & Requirements Analysis</div>
        </div>
        
        <!-- Executive Summary -->
        <div class="executive-summary">
            <h2 class="section-title"><i class="fas fa-chart-line"></i> Executive Summary</h2>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value score-{overall_metrics['overall_rating'].lower()}">{overall_metrics['overall_score']}/10</div>
                    <div class="metric-label">Overall Quality Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics['files_analyzed']}</div>
                    <div class="metric-label">Files Analyzed</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics['total_issues']}</div>
                    <div class="metric-label">Standards Issues</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value score-{overall_metrics['requirements_rating'].lower()}">{round(overall_metrics['requirements_score'], 2)}%</div>
                    <div class="metric-label">Requirements Coverage</div>
                </div>
            </div>
        </div>
        
        {self._generate_yaml_spec_section(analysis_data['yaml_spec'])}
        {self._generate_requirements_section(analysis_data['requirements'])}
        {self._generate_standards_section(analysis_data['standards'])}
        {self._generate_deep_eval_section(analysis_data['deep_eval'])}
        {self._generate_recommendations_section(overall_metrics['recommendations'])}
        
        <!-- Footer -->
        <div class="footer">
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
            <p>This report provides automated analysis and recommendations. Manual review is recommended for critical systems.</p>
        </div>
    </div>

    <script>
        // Expandable section functionality
        document.querySelectorAll('.expandable-header').forEach(header => {{
            header.addEventListener('click', function() {{
                const content = this.nextElementSibling;
                const icon = this.querySelector('.expandable-icon');
                
                content.classList.toggle('expanded');
                icon.style.transform = content.classList.contains('expanded') ? 'rotate(180deg)' : 'rotate(0deg)';
            }});
        }});

        // Auto-expand sections with errors
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.expandable-section').forEach(section => {{
                const header = section.querySelector('.expandable-header');
                const content = section.querySelector('.expandable-content');
                const hasIssues = content.querySelector('.tool-output')?.textContent.includes('Issue:') || 
                                content.querySelector('.requirement-missing') ||
                                content.querySelector('.requirement-partial') ||
                                content.querySelector('.violation-item');
                
                if (hasIssues) {{
                    content.classList.add('expanded');
                    const icon = header.querySelector('.expandable-icon');
                    icon.style.transform = 'rotate(180deg)';
                }}
            }});
        }});
    </script>
</body>
</html>
        """
        return html_content
    
    def _generate_yaml_spec_section(self, yaml_spec_data: Dict) -> str:
        """Generate YAML specification analysis section"""
        if not yaml_spec_data.get("available", False):
            if yaml_spec_data.get("error"):
                return f'''
                <div class="section">
                    <h2 class="section-title"><i class="fas fa-file-contract"></i> YAML Specification Analysis</h2>
                    <div class="status-badge status-error">ERROR</div>
                    <p style="margin-top: 1rem; color: #6b7280;">{yaml_spec_data.get("error", "Unknown error")}</p>
                </div>
                '''
            return '''
            <div class="section">
                <h2 class="section-title"><i class="fas fa-file-contract"></i> YAML Specification Analysis</h2>
                <div class="status-badge status-info">NOT PERFORMED</div>
                <p style="margin-top: 1rem; color: #6b7280;">No YAML specification analysis data available.</p>
            </div>
            '''
        
        specification_used = yaml_spec_data.get("specification_used", {})
        validation_steps = yaml_spec_data.get("validation_steps", {})
        overall_metrics = yaml_spec_data.get("overall_metrics", {})
        
        compliance_score = overall_metrics.get('overall_compliance_score', 0)
        total_violations = overall_metrics.get('total_violations_found', 0)
        compliance_level = overall_metrics.get('compliance_level', 'UNKNOWN')
        
        # Generate category sections
        category_sections = ""
        for category_name, category_data in validation_steps.items():
            category_sections += self._generate_yaml_category_section(category_name, category_data)
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-file-contract"></i> YAML Specification Analysis</h2>
            
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value score-{compliance_level.lower()}">{compliance_score}%</div>
                    <div class="metric-label">Compliance Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics.get('total_categories_validated', 0)}</div>
                    <div class="metric-label">Categories</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics.get('total_yaml_rules_applied', 0)}</div>
                    <div class="metric-label">Rules Applied</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{total_violations}</div>
                    <div class="metric-label">Total Violations</div>
                </div>
            </div>
            
            <div style="text-align: center; margin: 1.5rem 0;">
                <div class="status-badge status-{'success' if compliance_score >= 80 else 'warning' if compliance_score >= 60 else 'error'}">
                    Specification Compliance: {compliance_score}% ({compliance_level})
                </div>
            </div>
            
            <!-- Specification Information -->
            <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem; color: #1e40af;">Specification Details</h4>
                <p><strong>Name:</strong> {specification_used.get('name', 'Unknown Specification')}</p>
                <p><strong>Version:</strong> {specification_used.get('version', 'N/A')}</p>
                <p><strong>Description:</strong> {specification_used.get('description', 'No description available')}</p>
                <p><strong>Last Updated:</strong> {specification_used.get('last_updated', 'N/A')}</p>
            </div>
            
            {category_sections}
        </div>
        """
    
    def _generate_yaml_category_section(self, category_name: str, category_data: Dict) -> str:
        """Generate HTML for a single YAML validation category"""
        json_analysis = category_data.get('json_analysis', {})
        streaming_analysis = category_data.get('streaming_analysis', {})
        
        compliance_score = json_analysis.get('overall_compliance_score', 0)
        violations = json_analysis.get('detailed_violations', [])
        summary = json_analysis.get('summary', '')
        
        # Generate violations HTML
        violations_html = ""
        for violation in violations:
            severity = violation.get('severity', 'medium')
            violations_html += f"""
            <div class="violation-item violation-{severity}">
                <div class="severity-badge severity-{severity}">{severity.upper()}</div>
                <strong>{violation.get('yaml_rule_name', 'Unknown Rule')}</strong>
                <div style="margin-top: 0.5rem;">
                    <strong>File:</strong> {violation.get('file', 'Unknown')} | 
                    <strong>Line:</strong> {violation.get('line', 'Unknown')}
                </div>
                <div style="margin-top: 0.5rem;">
                    <strong>Description:</strong> {violation.get('violation_description', 'No description')}
                </div>
                <div style="margin-top: 0.5rem;">
                    <strong>Suggestion:</strong> {violation.get('suggestion', 'No suggestion')}
                </div>
            </div>
            """
        
        # Generate streaming analysis HTML
        streaming_html = ""
        streaming_content = streaming_analysis.get('streaming_content', '')
        if streaming_content:
            streaming_html = f"""
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-comment-alt"></i>
                        View Detailed Analysis
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        <div class="tool-output">{streaming_content}</div>
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="expandable-section">
            <div class="expandable-header">
                <div class="expandable-title">
                    <i class="fas fa-folder"></i>
                    {category_name.replace('_', ' ').title()} ({len(violations)} violations)
                </div>
                <i class="fas fa-chevron-down expandable-icon"></i>
            </div>
            <div class="expandable-content">
                <div class="tool-results">
                    <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                        <div class="status-badge status-{'success' if compliance_score >= 80 else 'warning' if compliance_score >= 60 else 'error'}">
                            Compliance: {compliance_score}%
                        </div>
                    </div>
                    
                    {summary and f'<div style="background: #f8fafc; padding: 1rem; border-radius: 6px; margin-bottom: 1rem;"><strong>Summary:</strong> {summary}</div>' or ''}
                    
                    {violations_html if violations_html else '''
                    <div style="text-align: center; padding: 2rem; color: #6b7280;">
                        <i class="fas fa-check-circle" style="font-size: 2rem; color: var(--success); margin-bottom: 1rem;"></i>
                        <p>No violations found in this category.</p>
                    </div>
                    '''}
                    
                    {streaming_html}
                </div>
            </div>
        </div>
        """
        
    def _generate_requirements_section(self, requirements_data: Dict) -> str:
        """Generate requirements validation section with expandable details for categorized requirements"""
        if not requirements_data.get("available", False):
            if requirements_data.get("skipped"):
                return '''
                <div class="section">
                    <h2 class="section-title"><i class="fas fa-tasks"></i> Requirements Validation</h2>
                    <div class="status-badge status-info">NOT PERFORMED</div>
                    <p style="margin-top: 1rem; color: #6b7280;">No requirements were provided for validation.</p>
                </div>
                '''
            else:
                error_msg = requirements_data.get("error", "Unknown error")
                return f'''
                <div class="section">
                    <h2 class="section-title"><i class="fas fa-tasks"></i> Requirements Validation</h2>
                    <div class="status-badge status-error">ERROR</div>
                    <p style="margin-top: 1rem; color: #6b7280;">{error_msg}</p>
                </div>
                '''
        
        # Extract data from the new structure
        comprehensive_analysis = requirements_data.get("comprehensive_analysis", {})
        alignment_scores = comprehensive_analysis.get("overall_alignment_scores", {})
        
        # Calculate overall metrics
        user_stories = alignment_scores.get("user_stories", {})
        functional_reqs = alignment_scores.get("functional_requirements", {})
        security_reqs = alignment_scores.get("security_requirements", {})
        non_functional_reqs = alignment_scores.get("non_functional_requirements", {})
        
        # Calculate totals
        total_requirements = (
            user_stories.get("total", 0) + 
            functional_reqs.get("total", 0) + 
            security_reqs.get("total", 0) +
            non_functional_reqs.get("total", 0)
        )
        
        total_implemented = (
            user_stories.get("implemented", 0) + 
            functional_reqs.get("implemented", 0) + 
            security_reqs.get("implemented", 0) +
            non_functional_reqs.get("implemented", 0)
        )
        
        total_not_implemented = (
            user_stories.get("not_implemented", 0) + 
            functional_reqs.get("not_implemented", 0) + 
            security_reqs.get("not_implemented", 0) +
            non_functional_reqs.get("not_implemented", 0)
        )
        
        # Get overall score from the extracted data
        overall_score = requirements_data.get("overall_score", 0)
        
        # Calculate coverage percentages
        implemented_pct = (total_implemented / total_requirements * 100) if total_requirements > 0 else 0
        not_implemented_pct = (total_not_implemented / total_requirements * 100) if total_requirements > 0 else 0
        
        # Generate category cards
        category_cards = ""
        for category_name, category_data in alignment_scores.items():
            if isinstance(category_data, dict) and category_data.get("total", 0) > 0:
                implemented = category_data.get("implemented", 0)
                not_implemented = category_data.get("not_implemented", 0)
                confidence = category_data.get("average_confidence_score", 0)
                
                category_cards += f"""
                <div class="metric-card">
                    <div class="metric-value score-{'excellent' if confidence >= 80 else 'good' if confidence >= 60 else 'fair' if confidence >= 40 else 'poor'}">{confidence:.1f}%</div>
                    <div class="metric-label">{category_name.replace('_', ' ').title()}</div>
                    <div class="metric-subtext">{implemented}/{category_data['total']} implemented</div>
                </div>
                """
        
        # Generate risk assessment
        risks = comprehensive_analysis.get("risks", {})
        risk_html = ""
        for risk_type, risk_desc in risks.items():
            if isinstance(risk_desc, str):
                risk_level = "error" if "critical" in risk_desc.lower() or "high" in risk_desc.lower() else "warning"
                risk_html += f"""
                <div class="requirement-item requirement-{risk_level}">
                    <strong>{risk_type.replace('_', ' ').title()}:</strong> {risk_desc}
                </div>
                """
        
        # Generate recommendations
        recommendations = comprehensive_analysis.get("recommendations", {})
        rec_html = ""
        for rec_type, rec_desc in recommendations.items():
            if isinstance(rec_desc, str):
                rec_html += f"""
                <div class="requirement-item">
                    <strong>{rec_type.replace('_', ' ').title()}:</strong> {rec_desc}
                </div>
                """
        
        # Generate improvement plans
        improvement_plans = comprehensive_analysis.get("actionable_improvement_plans", {})
        plan_html = ""
        for plan_type, plan_desc in improvement_plans.items():
            if isinstance(plan_desc, str):
                plan_html += f"""
                <div class="requirement-item">
                    <strong>{plan_type.replace('_', ' ').title()}:</strong> {plan_desc}
                </div>
                """
        
        # Executive summary
        exec_summary = comprehensive_analysis.get("executive_summary", "No executive summary available.")
        code_quality = comprehensive_analysis.get("code_quality_evaluation", "No quality evaluation available.")
        
        # Requirement details
        requirement_details = comprehensive_analysis.get("requirement_details", {})
        user_story_details = requirement_details.get("user_stories", [])
        functional_details = requirement_details.get("functional_requirements", [])
        security_details = requirement_details.get("security_requirements", [])
        
        # Generate requirement details HTML
        requirement_details_html = self._generate_requirement_details_html(requirement_details)
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-tasks"></i> Requirements Validation</h2>
            
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value score-{'excellent' if overall_score >= 80 else 'good' if overall_score >= 60 else 'fair' if overall_score >= 40 else 'poor'}">{overall_score:.1f}%</div>
                    <div class="metric-label">Overall Alignment</div>
                </div>
                {category_cards}
            </div>
            
            <div style="text-align: center; margin: 1.5rem 0;">
                <div class="status-badge status-{'success' if overall_score >= 80 else 'warning' if overall_score >= 60 else 'error'}">
                    Overall Implementation: {overall_score:.1f}%
                </div>
            </div>
            
            <div style="background: #f8fafc; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem;">Implementation Summary:</h4>
                <p><strong>Total Requirements:</strong> {total_requirements}</p>
                <p><strong>Implemented:</strong> {total_implemented} requirements ({implemented_pct:.1f}%)</p>
                <p><strong>Not Implemented:</strong> {total_not_implemented} requirements ({not_implemented_pct:.1f}%)</p>
            </div>

            <!-- Executive Summary -->
            <div style="background: #f0f9ff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem; color: #1e40af;">📋 Executive Summary</h4>
                <p style="color: #374151; line-height: 1.6;">{exec_summary}</p>
            </div>

            <!-- Code Quality -->
            <div style="background: #fef7ed; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 1rem; color: #ea580c;">🏗️ Code Quality Evaluation</h4>
                <p style="color: #374151; line-height: 1.6;">{code_quality}</p>
            </div>
            
            <!-- Expandable Requirement Details -->
            {requirement_details_html}
            
            <!-- Expandable Risk Assessment -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        View Risk Assessment
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        <h4>Risk Assessment</h4>
                        {risk_html if risk_html else '<p>No risk assessment available</p>'}
                    </div>
                </div>
            </div>

            <!-- Expandable Recommendations -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-lightbulb"></i>
                        View Recommendations
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        <h4>Recommendations by Category</h4>
                        {rec_html if rec_html else '<p>No recommendations available</p>'}
                    </div>
                </div>
            </div>

            <!-- Expandable Improvement Plans -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-road"></i>
                        View Improvement Plans
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        <h4>Actionable Improvement Plans</h4>
                        {plan_html if plan_html else '<p>No improvement plans available</p>'}
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_requirement_details_html(self, requirement_details: Dict) -> str:
        """Generate HTML for detailed requirement analysis"""
        html_sections = []
        
        for category, requirements in requirement_details.items():
            if requirements and isinstance(requirements, list):
                category_html = f"""
                <div class="expandable-section">
                    <div class="expandable-header">
                        <div class="expandable-title">
                            <i class="fas fa-list-check"></i>
                            View {category.replace('_', ' ').title()} Details
                        </div>
                        <i class="fas fa-chevron-down expandable-icon"></i>
                    </div>
                    <div class="expandable-content">
                        <div class="tool-results">
                            <h4>{category.replace('_', ' ').title()} Analysis</h4>
                """
                
                for req in requirements:
                    if isinstance(req, dict):
                        req_id = req.get("id", "Unknown")
                        description = req.get("description", "No description")
                        status = req.get("status", "Unknown")
                        confidence = req.get("confidence_score", 0)
                        implemented_files = req.get("implemented_files", [])
                        code_evidence = req.get("code_evidence", "No evidence")
                        gaps = req.get("gaps", "None")
                        
                        status_class = "requirement-item"
                        if "Not Implemented" in status:
                            status_class = "requirement-item requirement-missing"
                        elif "Partially" in status:
                            status_class = "requirement-item requirement-partial"
                        
                        category_html += f"""
                        <div class="{status_class}">
                            <strong>{req_id}: {description}</strong><br>
                            <strong>Status:</strong> {status} | <strong>Confidence:</strong> {confidence}%<br>
                            <strong>Implemented in:</strong> {', '.join(implemented_files) if implemented_files else 'None'}<br>
                            <strong>Code Evidence:</strong> {code_evidence}<br>
                            <strong>Gaps:</strong> {gaps}
                        </div>
                        """
                
                category_html += """
                        </div>
                    </div>
                </div>
                """
                html_sections.append(category_html)
        
        return "\n".join(html_sections)
    
    def _generate_standards_section(self, standards_data: Dict) -> str:
        """Generate standards analysis section with expandable details"""
        if not standards_data.get("available", False):
            return '''
            <div class="section">
                <h2 class="section-title"><i class="fas fa-ruler"></i> Code Standards Analysis</h2>
                <p>No standards analysis data available.</p>
            </div>
            '''
        
        files = standards_data.get("files", [])
        total_issues = standards_data.get("total_issues", 0)
        
        # Generate file issues list
        file_issues_html = ""
        if files:
            file_issues_html = "<div class='file-list'><h4>File Analysis:</h4>"
            for file_data in files:
                file_name = file_data.get("file_name", "Unknown")
                file_issues = file_data.get("issue_count", 0)
                
                file_issues_html += f"""
                <div class="file-item">
                    <div class="file-name">
                        <i class="fas fa-file-code"></i>
                        {file_name}
                    </div>
                    <div class="file-stats">
                        <span class="status-badge status-{'error' if file_issues > 5 else 'warning' if file_issues > 2 else 'info'}">{file_issues} issues</span>
                    </div>
                </div>
                """
            file_issues_html += "</div>"
        
        # Generate detailed tool results for each file
        detailed_analysis_html = ""
        for file_data in files:
            file_name = file_data.get("file_name", "Unknown")
            tool_results = file_data.get("tool_results", [])
            
            file_tools_html = ""
            for tool_result in tool_results:
                tool_name = tool_result.get("tool", "Unknown")
                result = tool_result.get("result", "")
                
                if result and "No issues" not in result and "No output" not in result:
                    file_tools_html += f"""
                    <div class="tool-result">
                        <div class="tool-name">{tool_name}</div>
                        <div class="tool-output">{result}</div>
                    </div>
                    """
            
            if file_tools_html:
                detailed_analysis_html += f"""
                <div style="margin-bottom: 2rem;">
                    <h4>{file_name}</h4>
                    {file_tools_html}
                </div>
                """
        
        if total_issues == 0:
            return f'''
            <div class="section">
                <h2 class="section-title"><i class="fas fa-ruler"></i> Code Standards Analysis</h2>
                <div class="status-badge status-success">EXCELLENT</div>
                <p style="margin-top: 1rem; color: #6b7280;">No code standards issues found. Excellent work!</p>
            </div>
            '''
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-ruler"></i> Code Standards Analysis</h2>
            <div class="status-badge status-{'error' if total_issues > 10 else 'warning'}">
                {total_issues} ISSUES FOUND
            </div>
            <p style="margin-top: 1rem; color: #6b7280;">
                Found {total_issues} code standards issues across {len(files)} files.
            </p>
            
            {file_issues_html}
            
            <!-- Expandable Tool Results -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-code"></i>
                        View Detailed Standards Analysis
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        {detailed_analysis_html if detailed_analysis_html else '<p>No detailed analysis available</p>'}
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_deep_eval_section(self, deep_eval_data: Dict) -> str:
        """Generate deep evaluation section with expandable details"""
        if not deep_eval_data.get("available", False):
            return ''  # Return empty string instead of the section
        
        overall_score = deep_eval_data.get("overall_score", 0)
        file_evaluations = deep_eval_data.get("file_evaluations", [])
        summary = deep_eval_data.get("summary", "")
        
        # Generate file evaluations
        file_eval_html = ""
        for file_eval in file_evaluations:
            file_name = file_eval.get("file_name", "Unknown")
            file_score = file_eval.get("overall_score", 0)
            metrics = file_eval.get("metrics", {})
            
            metrics_html = ""
            for metric_name, metric_data in metrics.items():
                score = metric_data.get("score", 0)
                reasoning = metric_data.get("reasoning", "")
                
                metrics_html += f"""
                <div style="margin-bottom: 1rem;">
                    <strong>{metric_name.replace('_', ' ').title()}:</strong> {score}/5.0
                    <br><small>{reasoning[:200]}{'...' if len(reasoning) > 200 else ''}</small>
                </div>
                """
            
            file_eval_html += f"""
            <div class="file-item">
                <div class="file-name">
                    <i class="fas fa-file-code"></i>
                    {file_name}
                </div>
                <div class="file-stats">
                    <span class="status-badge status-{'success' if file_score >= 4 else 'warning' if file_score >= 3 else 'error'}">{file_score}/5.0</span>
                </div>
            </div>
            <div style="padding: 1rem; background: #f8fafc; border-radius: 6px; margin-bottom: 1rem;">
                {metrics_html}
            </div>
            """
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-microscope"></i> Deep Quality Evaluation</h2>
            
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value score-{'excellent' if overall_score >= 4 else 'good' if overall_score >= 3 else 'fair' if overall_score >= 2 else 'poor'}">{overall_score}/5</div>
                    <div class="metric-label">Overall Quality</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{len(file_evaluations)}</div>
                    <div class="metric-label">Files Evaluated</div>
                </div>
            </div>
            
            {f'<div style="background: #f0f9ff; padding: 1.5rem; border-radius: 8px; margin-top: 1rem;"><h4>Summary:</h4><p>{summary}</p></div>' if summary else ''}
            
            <!-- Expandable File Evaluations -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-chart-bar"></i>
                        View Detailed Quality Evaluation
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        {file_eval_html if file_eval_html else '<p>No detailed evaluation data available</p>'}
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_recommendations_section(self, recommendations: List[str]) -> str:
        """Generate recommendations section"""
        if not recommendations:
            return '''
            <div class="section">
                <h2 class="section-title"><i class="fas fa-lightbulb"></i> Recommendations</h2>
                <p>No specific recommendations available.</p>
            </div>
            '''
        
        recommendations_html = "".join([f"<li style='margin-bottom: 0.5rem;'>{rec}</li>" for rec in recommendations])
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-lightbulb"></i> Key Recommendations</h2>
            <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 8px;">
                <ul style="list-style-position: inside;">
                    {recommendations_html}
                </ul>
            </div>
        </div>
        """
        
    def _calculate_overall_metrics(self, analysis_data: Dict) -> Dict:
        """Calculate overall metrics from all analyses - UPDATED for new structure"""
        metrics = {
            'files_analyzed': analysis_data.get('files_analyzed', 0),
            'total_issues': analysis_data['standards'].get('total_issues', 0),
            'requirements_score': 0,
            'overall_score': 0,
            'overall_rating': 'UNKNOWN',
            'requirements_rating': 'UNKNOWN',
            'recommendations': []
        }
        
        # Requirements score from new structure
        if analysis_data['requirements'].get('available', False):
            metrics['requirements_score'] = analysis_data['requirements'].get('overall_score', 0)
        
        # Deep evaluation score (only use if available)
        if analysis_data['deep_eval'].get('available', False):
            deep_score = analysis_data['deep_eval'].get('overall_score', 0)
            metrics['overall_score'] = round(deep_score * 2, 1)  # Convert 5-point scale to 10-point
        
        # If no deep eval, calculate from requirements and standards
        if metrics['overall_score'] == 0 and analysis_data['requirements'].get('available', False):
            # Base score on requirements coverage and standards issues
            req_score = metrics['requirements_score'] / 10  # Convert to 10-point scale
            standards_penalty = min(metrics['total_issues'] * 0.2, 3)  # Penalty for standards issues
            metrics['overall_score'] = max(0, req_score - standards_penalty)
        
        # Determine ratings
        if metrics['overall_score'] >= 8:
            metrics['overall_rating'] = 'EXCELLENT'
        elif metrics['overall_score'] >= 6:
            metrics['overall_rating'] = 'GOOD'
        elif metrics['overall_score'] >= 4:
            metrics['overall_rating'] = 'FAIR'
        else:
            metrics['overall_rating'] = 'POOR'
        
        if metrics['requirements_score'] >= 80:
            metrics['requirements_rating'] = 'EXCELLENT'
        elif metrics['requirements_score'] >= 60:
            metrics['requirements_rating'] = 'GOOD'
        elif metrics['requirements_score'] >= 40:
            metrics['requirements_rating'] = 'FAIR'
        else:
            metrics['requirements_rating'] = 'POOR'
        
        # Generate recommendations
        metrics['recommendations'] = self._generate_recommendations(analysis_data)
        
        return metrics
    
    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Standards recommendations
        if analysis_data['standards']['total_issues'] > 0:
            recommendations.append(f"Address {analysis_data['standards']['total_issues']} coding standards issues")
        
        # Requirements recommendations
        if analysis_data['requirements'].get('available', False):
            req_data = analysis_data['requirements']
            if req_data.get('coverage_percentage', 0) < 80:
                recommendations.append(f"Improve requirements coverage (currently {req_data['coverage_percentage']:.1f}%)")
        
        # Deep evaluation recommendations
        if analysis_data['deep_eval'].get('available', False):
            deep_data = analysis_data['deep_eval']
            if deep_data.get('overall_score', 0) < 3:
                recommendations.append("Address code quality issues identified in deep evaluation")
        
        # YAML spec recommendations
        if analysis_data['yaml_spec'].get('available', False):
            yaml_data = analysis_data['yaml_spec']
            overall_metrics = yaml_data.get('overall_metrics', {})
            total_violations = overall_metrics.get('total_violations_found', 0)
            if total_violations > 0:
                recommendations.append(f"Fix {total_violations} YAML specification violations")
        
        if not recommendations:
            recommendations.append("No critical issues found. Maintain current code quality standards.")
        
        return recommendations
    
    def _generate_detailed_json_summary(self, analysis_data: Dict) -> Dict:
        """Generate detailed JSON summary with all analysis data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_metrics": self._calculate_overall_metrics(analysis_data),
            "requirements_analysis": analysis_data['requirements'],
            "standards_analysis": analysis_data['standards'],
            "deep_evaluation": analysis_data['deep_eval'],
            "yaml_spec_analysis": analysis_data['yaml_spec'],
            "files_analyzed": analysis_data['files_analyzed']
        }
    
    def get_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="Consolidated Reporter",
            func=self.generate_consolidated_report,
            description="Generates comprehensive HTML reports from code analysis tools."
        )