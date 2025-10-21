# enhanced_yaml_spec_reporter.py
import os
import json
from datetime import datetime
from typing import Dict, List, Any

class EnhancedYAMLSpecReporter:
    """
    Generates comprehensive HTML reports for YAML specification validation results.
    Enhanced with better CSS and interactive features.
    """
    
    def __init__(self, output_dir: str = "code_review_reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_yaml_spec_report(self, yaml_spec_data: Dict) -> Dict:
        """Generate comprehensive HTML report from YAML specification analysis"""
        print("📋 Generating YAML Specification HTML report...")
        
        try:
            # Create report directory
            report_dir = os.path.join(self.output_dir, f"yaml_spec_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate comprehensive HTML report
            html_content = self._create_enhanced_yaml_spec_html(yaml_spec_data)
            html_file = os.path.join(report_dir, "yaml_specification_analysis.html")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate JSON summary
            json_file = os.path.join(report_dir, "yaml_specification_analysis.json")
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(yaml_spec_data, f, indent=2, ensure_ascii=False)
            
            # Return paths
            result_state = {
                "yaml_spec_html_report_path": html_file,
                "yaml_spec_report_directory": report_dir,
                "yaml_spec_json_path": json_file
            }
            
            print(f"✅ YAML Specification HTML report generated: {html_file}")
            return result_state
            
        except Exception as e:
            error_state = {"error": f"YAML spec report generation failed: {str(e)}"}
            print(f"❌ YAML spec report generation error: {e}")
            return error_state
    
    def _create_enhanced_yaml_spec_html(self, yaml_spec_data: Dict) -> str:
        """Create enhanced HTML report for YAML specification analysis"""
        
        overall_metrics = yaml_spec_data.get("overall_metrics", {})
        validation_steps = yaml_spec_data.get("validation_steps", {})
        specification_used = yaml_spec_data.get("specification_used", {})
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YAML Specification Compliance Report</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #3b82f6;
            --primary-dark: #1d4ed8;
            --secondary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --critical: #dc2626;
            --info: #06b6d4;
            --background: #f8fafc;
            --surface: #ffffff;
            --text: #1f2937;
            --text-light: #6b7280;
            --border: #e5e7eb;
            --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: var(--surface);
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 100" fill="rgba(255,255,255,0.1)"><polygon points="0,0 1000,50 1000,100 0,100"/></svg>');
            background-size: cover;
        }}
        
        .header-content {{
            position: relative;
            z-index: 2;
        }}
        
        .header h1 {{
            font-size: 2.75rem;
            margin-bottom: 0.75rem;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header .subtitle {{
            font-size: 1.3rem;
            opacity: 0.95;
            font-weight: 400;
            margin-bottom: 1rem;
        }}
        
        .header-badges {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1.5rem;
        }}
        
        /* Executive Summary */
        .executive-summary {{
            padding: 2.5rem;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .metric-card {{
            background: var(--surface);
            padding: 2rem 1.5rem;
            border-radius: 16px;
            text-align: center;
            box-shadow: var(--shadow);
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }}
        
        .metric-card:hover {{
            transform: translateY(-8px);
            box-shadow: var(--shadow-lg);
        }}
        
        .metric-value {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            line-height: 1;
        }}
        
        .metric-label {{
            color: var(--text-light);
            font-weight: 500;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }}
        
        .metric-subtext {{
            font-size: 0.85rem;
            color: var(--text-light);
            margin-top: 0.5rem;
        }}
        
        .score-excellent {{ color: var(--success); }}
        .score-good {{ color: var(--primary); }}
        .score-fair {{ color: var(--warning); }}
        .score-poor {{ color: var(--error); }}
        
        /* Severity Progress */
        .severity-progress {{
            margin-top: 2rem;
        }}
        
        .progress-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .progress-item {{
            background: var(--surface);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid;
            box-shadow: var(--shadow);
        }}
        
        .progress-critical {{ border-left-color: var(--critical); background: linear-gradient(135deg, #fef2f2, #fff); }}
        .progress-high {{ border-left-color: var(--error); background: linear-gradient(135deg, #fef2f2, #fff); }}
        .progress-medium {{ border-left-color: var(--warning); background: linear-gradient(135deg, #fffbeb, #fff); }}
        .progress-low {{ border-left-color: var(--info); background: linear-gradient(135deg, #f0f9ff, #fff); }}
        
        /* Sections */
        .section {{
            padding: 2.5rem;
            border-bottom: 1px solid var(--border);
            transition: all 0.3s ease;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section-title {{
            font-size: 1.75rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border);
        }}
        
        .section-title i {{
            font-size: 1.5rem;
            color: var(--primary);
        }}
        
        /* Status Badges */
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            box-shadow: var(--shadow);
        }}
        
        .status-success {{ background: var(--success); color: white; }}
        .status-warning {{ background: var(--warning); color: white; }}
        .status-error {{ background: var(--error); color: white; }}
        .status-info {{ background: var(--info); color: white; }}
        .status-critical {{ background: var(--critical); color: white; }}
        
        /* Expandable Sections */
        .expandable-section {{
            margin-top: 1.5rem;
            border: 1px solid var(--border);
            border-radius: 12px;
            overflow: hidden;
            transition: all 0.3s ease;
        }}
        
        .expandable-section:hover {{
            box-shadow: var(--shadow);
        }}
        
        .expandable-header {{
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            padding: 1.25rem 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
            border-bottom: 1px solid transparent;
        }}
        
        .expandable-header:hover {{
            background: linear-gradient(135deg, #f1f5f9, #e2e8f0);
        }}
        
        .expandable-header.expanded {{
            border-bottom-color: var(--border);
            background: var(--surface);
        }}
        
        .expandable-title {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 600;
            color: var(--text);
        }}
        
        .expandable-icon {{
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            color: var(--text-light);
        }}
        
        .expandable-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            background: white;
        }}
        
        .expandable-content.expanded {{
            max-height: 2000px;
        }}
        
        .tool-results {{
            padding: 1.5rem;
            background: white;
        }}
        
        /* Violation Items */
        .violation-item {{
            padding: 1.25rem;
            margin-bottom: 0.75rem;
            border-radius: 10px;
            border-left: 5px solid;
            background: var(--surface);
            box-shadow: var(--shadow);
            transition: all 0.3s ease;
            border: 1px solid var(--border);
        }}
        
        .violation-item:hover {{
            transform: translateX(4px);
            box-shadow: var(--shadow-lg);
        }}
        
        .violation-critical {{
            border-left-color: var(--critical);
            background: linear-gradient(135deg, #fef2f2, #fff);
        }}
        
        .violation-high {{
            border-left-color: var(--error);
            background: linear-gradient(135deg, #fef2f2, #fff);
        }}
        
        .violation-medium {{
            border-left-color: var(--warning);
            background: linear-gradient(135deg, #fffbeb, #fff);
        }}
        
        .violation-low {{
            border-left-color: var(--info);
            background: linear-gradient(135deg, #f0f9ff, #fff);
        }}
        
        .violation-severity {{
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.35rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .severity-critical {{ background: var(--critical); color: white; }}
        .severity-high {{ background: var(--error); color: white; }}
        .severity-medium {{ background: var(--warning); color: white; }}
        .severity-low {{ background: var(--info); color: white; }}
        
        /* File List */
        .file-list {{
            margin: 1.5rem 0;
        }}
        
        .file-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.25rem;
            border: 1px solid var(--border);
            border-radius: 10px;
            margin-bottom: 0.5rem;
            background: var(--surface);
            transition: all 0.3s ease;
        }}
        
        .file-item:hover {{
            background: #f8fafc;
            transform: translateX(4px);
        }}
        
        .file-name {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-weight: 500;
        }}
        
        .file-name i {{
            color: var(--primary);
        }}
        
        /* Streaming Analysis */
        .streaming-analysis {{
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 1.5rem;
            border-radius: 10px;
            font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-top: 1rem;
            border: 1px solid #333;
            max-height: 500px;
            overflow-y: auto;
        }}
        
        .streaming-analysis::-webkit-scrollbar {{
            width: 8px;
        }}
        
        .streaming-analysis::-webkit-scrollbar-track {{
            background: #2d2d2d;
            border-radius: 4px;
        }}
        
        .streaming-analysis::-webkit-scrollbar-thumb {{
            background: #555;
            border-radius: 4px;
        }}
        
        .streaming-analysis::-webkit-scrollbar-thumb:hover {{
            background: #777;
        }}
        
        /* Progress Bars */
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
            margin: 0.5rem 0;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}
        
        .progress-critical .progress-fill {{ background: var(--critical); }}
        .progress-high .progress-fill {{ background: var(--error); }}
        .progress-medium .progress-fill {{ background: var(--warning); }}
        .progress-low .progress-fill {{ background: var(--info); }}
        
        /* Footer */
        .footer {{
            text-align: center;
            padding: 2.5rem;
            color: var(--text-light);
            font-size: 0.9rem;
            border-top: 1px solid var(--border);
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
        }}
        
        .footer-links {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        
        .footer-link {{
            color: var(--primary);
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .footer-link:hover {{
            color: var(--primary-dark);
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.6s ease-out;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .summary-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .section {{
                padding: 1.5rem;
            }}
            
            .progress-grid {{
                grid-template-columns: 1fr;
            }}
            
            body {{
                padding: 10px;
            }}
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
                border-radius: 0;
            }}
            
            .expandable-content {{
                max-height: none !important;
            }}
            
            .metric-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container fade-in">
        <!-- Header -->
        <div class="header">
            <div class="header-content">
                <h1><i class="fas fa-file-contract"></i> YAML Specification Compliance Report</h1>
                <div class="subtitle">Comprehensive Code Quality & Standards Validation Analysis</div>
                <div class="header-badges">
                    <div class="status-badge status-info">
                        <i class="fas fa-calendar"></i>
                        {datetime.now().strftime('%Y-%m-%d')}
                    </div>
                    <div class="status-badge status-{overall_metrics.get('compliance_level', 'POOR').lower()}">
                        <i class="fas fa-chart-bar"></i>
                        {overall_metrics.get('compliance_level', 'POOR')} Compliance
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Executive Summary -->
        <div class="executive-summary">
            <h2 class="section-title"><i class="fas fa-chart-line"></i> Executive Summary</h2>
            <div class="summary-grid">
                <div class="metric-card">
                    <div class="metric-value score-{overall_metrics.get('compliance_level', 'POOR').lower()}">{overall_metrics.get('overall_compliance_score', 0)}%</div>
                    <div class="metric-label">Overall Compliance Score</div>
                    <div class="metric-subtext">{overall_metrics.get('compliance_level', 'POOR')} Level</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics.get('total_categories_validated', 0)}</div>
                    <div class="metric-label">Categories Validated</div>
                    <div class="metric-subtext">Quality Dimensions</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics.get('total_yaml_rules_applied', 0)}</div>
                    <div class="metric-label">Rules Applied</div>
                    <div class="metric-subtext">Validation Criteria</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{overall_metrics.get('total_violations_found', 0)}</div>
                    <div class="metric-label">Total Violations</div>
                    <div class="metric-subtext">Issues Identified</div>
                </div>
            </div>
            
            <!-- Severity Progress -->
            <div class="severity-progress">
                <h4 style="margin-bottom: 1rem; color: var(--text);">Violations by Severity:</h4>
                <div class="progress-grid">
                    {self._generate_severity_progress(overall_metrics.get('violations_by_severity', {}))}
                </div>
            </div>
        </div>
        
        <!-- Specification Information -->
        <div class="section">
            <h2 class="section-title"><i class="fas fa-info-circle"></i> Specification Information</h2>
            <div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 2rem; border-radius: 12px; border-left: 5px solid var(--primary);">
                <h4 style="margin-bottom: 1rem; color: var(--primary-dark);">{specification_used.get('name', 'Unknown Specification')}</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                    <div>
                        <strong>Version:</strong> {specification_used.get('version', 'N/A')}
                    </div>
                    <div>
                        <strong>Last Updated:</strong> {specification_used.get('last_updated', 'N/A')}
                    </div>
                </div>
                <p style="margin-top: 1rem; color: var(--text);"><strong>Description:</strong> {specification_used.get('description', 'No description available')}</p>
            </div>
        </div>
        
        <!-- Detailed Analysis by Category -->
        {self._generate_validation_categories(validation_steps)}
        
        <!-- Recommendations -->
        {self._generate_recommendations_section(overall_metrics)}
        
        <!-- Footer -->
        <div class="footer">
            <p>Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}</p>
            <p>This report provides automated analysis based on YAML specification validation. Manual review is recommended for critical systems.</p>
            <div class="footer-links">
                <span class="footer-link"><i class="fas fa-download"></i> Export as JSON</span>
                <span class="footer-link"><i class="fas fa-print"></i> Print Report</span>
                <span class="footer-link"><i class="fas fa-question-circle"></i> Help & Documentation</span>
            </div>
        </div>
    </div>

    <script>
        // Enhanced expandable section functionality
        document.querySelectorAll('.expandable-header').forEach(header => {{
            header.addEventListener('click', function() {{
                const content = this.nextElementSibling;
                const icon = this.querySelector('.expandable-icon');
                
                // Toggle expanded state
                content.classList.toggle('expanded');
                this.classList.toggle('expanded');
                icon.style.transform = content.classList.contains('expanded') ? 'rotate(180deg)' : 'rotate(0deg)';
                
                // Add smooth scrolling to expanded content
                if (content.classList.contains('expanded')) {{
                    setTimeout(() => {{
                        content.scrollIntoView({{
                            behavior: 'smooth',
                            block: 'nearest'
                        }});
                    }}, 300);
                }}
            }});
        }});

        // Auto-expand sections with critical/high severity violations
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.expandable-section').forEach(section => {{
                const header = section.querySelector('.expandable-header');
                const content = section.querySelector('.expandable-content');
                const hasCriticalViolations = content.querySelector('.severity-critical') || 
                                           content.querySelector('.severity-high');
                
                if (hasCriticalViolations) {{
                    content.classList.add('expanded');
                    header.classList.add('expanded');
                    const icon = header.querySelector('.expandable-icon');
                    icon.style.transform = 'rotate(180deg)';
                }}
            }});
            
            // Add animation to metric cards
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach((card, index) => {{
                card.style.animationDelay = `${index * 0.1}s`;
                card.classList.add('fade-in');
            }});
        }});

        // Progress bar animation
        function animateProgressBars() {{
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {{
                const width = bar.style.width;
                bar.style.width = '0';
                setTimeout(() => {{
                    bar.style.width = width;
                }}, 100);
            }});
        }}

        // Initialize progress bar animation
        setTimeout(animateProgressBars, 500);

        // Print functionality
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {{
                e.preventDefault();
                window.print();
            }}
        }});

        // Add hover effects to violation items
        document.querySelectorAll('.violation-item').forEach(item => {{
            item.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateX(8px)';
            }});
            item.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateX(0)';
            }});
        }});

        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});

        // Add loading animation
        window.addEventListener('load', function() {{
            document.body.classList.add('loaded');
        }});
    </script>
</body>
</html>
        """
        return html_content
    
    def _generate_severity_progress(self, violations_by_severity: Dict) -> str:
        """Generate severity progress bars for the executive summary"""
        progress_items = []
        severity_config = {
            'critical': {'color': 'critical', 'icon': 'fas fa-fire', 'label': 'Critical'},
            'high': {'color': 'high', 'icon': 'fas fa-exclamation-triangle', 'label': 'High'},
            'medium': {'color': 'medium', 'icon': 'fas fa-exclamation-circle', 'label': 'Medium'},
            'low': {'color': 'low', 'icon': 'fas fa-info-circle', 'label': 'Low'}
        }
        
        total_violations = sum(violations_by_severity.values())
        
        for severity, config in severity_config.items():
            count = violations_by_severity.get(severity, 0)
            percentage = (count / total_violations * 100) if total_violations > 0 else 0
            
            progress_items.append(f"""
            <div class="progress-item progress-{config['color']}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <i class="{config['icon']}"></i>
                        <strong>{config['label']}</strong>
                    </div>
                    <span style="font-weight: 600;">{count}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {percentage}%"></div>
                </div>
                <div style="text-align: right; font-size: 0.8rem; color: var(--text-light); margin-top: 0.25rem;">
                    {percentage:.1f}%
                </div>
            </div>
            """)
        
        return ''.join(progress_items)
    
    def _generate_validation_categories(self, validation_steps: Dict) -> str:
        """Generate HTML for all validation categories"""
        categories_html = []
        
        for category_name, category_data in validation_steps.items():
            categories_html.append(self._generate_category_section(category_name, category_data))
        
        return '\n'.join(categories_html)
    
    def _generate_category_section(self, category_name: str, category_data: Dict) -> str:
        """Generate HTML for a single validation category"""
        json_analysis = category_data.get('json_analysis', {})
        streaming_analysis = category_data.get('streaming_analysis', {})
        yaml_rules = category_data.get('yaml_rules', [])
        
        compliance_score = json_analysis.get('overall_compliance_score', 0)
        violations = json_analysis.get('detailed_violations', [])
        files_analyzed = json_analysis.get('files_analyzed', [])
        summary = json_analysis.get('summary', '')
        
        # Determine category status and icon
        status_config = {
            'excellent': {'class': 'status-success', 'icon': 'fas fa-check-circle', 'min_score': 80},
            'good': {'class': 'status-info', 'icon': 'fas fa-check', 'min_score': 60},
            'fair': {'class': 'status-warning', 'icon': 'fas fa-exclamation-triangle', 'min_score': 40},
            'poor': {'class': 'status-error', 'icon': 'fas fa-times-circle', 'min_score': 0}
        }
        
        status = 'poor'
        for status_name, config in status_config.items():
            if compliance_score >= config['min_score']:
                status = status_name
                break
        
        status_class = status_config[status]['class']
        status_icon = status_config[status]['icon']
        
        # Generate violations HTML
        violations_html = ""
        for violation in violations:
            severity = violation.get('severity', 'medium')
            violations_html += f"""
            <div class="violation-item violation-{severity}">
                <div style="display: flex; justify-content: between; align-items: start; gap: 1rem; margin-bottom: 0.75rem;">
                    <span class="violation-severity severity-{severity}">
                        <i class="fas fa-{self._get_severity_icon(severity)}"></i>
                        {severity.upper()}
                    </span>
                    <div style="flex: 1;">
                        <strong style="color: var(--text);">{violation.get('yaml_rule_name', 'Unknown Rule')}</strong>
                        <div style="font-size: 0.85rem; color: var(--text-light); margin-top: 0.25rem;">
                            {violation.get('yaml_rule_id', '')}
                        </div>
                    </div>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <div style="display: flex; gap: 2rem; flex-wrap: wrap; font-size: 0.9rem;">
                        <div><strong>File:</strong> {violation.get('file', 'Unknown')}</div>
                        <div><strong>Line:</strong> {violation.get('line', 'Unknown')}</div>
                    </div>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <strong>Description:</strong> {violation.get('violation_description', 'No description')}
                </div>
                <div style="background: rgba(255,255,255,0.7); padding: 0.75rem; border-radius: 6px; border-left: 3px solid var(--primary);">
                    <strong>Suggestion:</strong> {violation.get('suggestion', 'No suggestion')}
                </div>
            </div>
            """
        
        # Generate files analyzed HTML
        files_html = ""
        if files_analyzed:
            files_html = "<div class='file-list'><h4>Files Analyzed:</h4>"
            for file in files_analyzed:
                files_html += f"""
                <div class="file-item">
                    <div class="file-name">
                        <i class="fas fa-file-code"></i>
                        {file}
                    </div>
                    <div style="color: var(--text-light); font-size: 0.9rem;">
                        <i class="fas fa-search"></i>
                    </div>
                </div>
                """
            files_html += "</div>"
        
        # Generate rules applied HTML
        rules_html = ""
        if yaml_rules:
            rules_html = f"""
            <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <strong>YAML Rules Applied:</strong>
                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem;">
                    {''.join([f'<span class="status-badge status-info" style="font-size: 0.75rem; padding: 0.25rem 0.5rem;">{rule}</span>' for rule in yaml_rules])}
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
                        View Detailed Rule Analysis
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="streaming-analysis">
                        {streaming_content}
                    </div>
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2 class="section-title">
                <i class="fas fa-{self._get_category_icon(category_name)}"></i>
                {category_name.replace('_', ' ').title()}
            </h2>
            
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
                <div class="status-badge {status_class}">
                    <i class="{status_icon}"></i>
                    {status.upper()}
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <strong>Compliance Score:</strong>
                    <span style="font-weight: 600; color: var(--{'success' if compliance_score >= 80 else 'primary' if compliance_score >= 60 else 'warning' if compliance_score >= 40 else 'error'});">
                        {compliance_score}%
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <strong>Violations:</strong>
                    <span style="font-weight: 600;">{len(violations)}</span>
                </div>
            </div>
            
            {rules_html}
            
            {files_html}
            
            {summary and f'<div style="background: linear-gradient(135deg, #f0f9ff, #e0f2fe); padding: 1.25rem; border-radius: 10px; margin-bottom: 1.5rem; border-left: 4px solid var(--info);"><strong>Summary:</strong> {summary}</div>' or ''}
            
            <!-- Violations Section -->
            <div class="expandable-section">
                <div class="expandable-header">
                    <div class="expandable-title">
                        <i class="fas fa-exclamation-triangle"></i>
                        View Violations ({len(violations)} found)
                    </div>
                    <i class="fas fa-chevron-down expandable-icon"></i>
                </div>
                <div class="expandable-content">
                    <div class="tool-results">
                        {violations_html if violations_html else '''
                        <div style="text-align: center; padding: 3rem; color: var(--text-light);">
                            <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 1rem;"></i>
                            <h3>No Violations Found</h3>
                            <p>Excellent! This category is fully compliant with the specification.</p>
                        </div>
                        '''}
                    </div>
                </div>
            </div>
            
            {streaming_html}
        </div>
        """
    
    def _get_severity_icon(self, severity: str) -> str:
        """Get icon for severity level"""
        icons = {
            'critical': 'fire',
            'high': 'exclamation-triangle',
            'medium': 'exclamation-circle',
            'low': 'info-circle'
        }
        return icons.get(severity, 'info-circle')
    
    def _get_category_icon(self, category_name: str) -> str:
        """Get icon for category"""
        icons = {
            'naming_conventions': 'tag',
            'code_structure': 'sitemap',
            'documentation': 'file-alt',
            'error_handling': 'bug',
            'security': 'shield-alt',
            'performance': 'tachometer-alt'
        }
        return icons.get(category_name, 'folder')
    
    def _generate_recommendations_section(self, overall_metrics: Dict) -> str:
        """Generate recommendations based on the analysis"""
        total_violations = overall_metrics.get('total_violations_found', 0)
        compliance_level = overall_metrics.get('compliance_level', 'POOR')
        violations_by_severity = overall_metrics.get('violations_by_severity', {})
        
        recommendations = []
        
        if compliance_level == 'POOR':
            recommendations.append("🚨 Immediate attention required: Code has significant compliance issues that need urgent resolution")
        
        critical_violations = violations_by_severity.get('critical', 0)
        if critical_violations > 0:
            recommendations.append(f"🔴 Address {critical_violations} critical security violations immediately to prevent potential vulnerabilities")
        
        high_violations = violations_by_severity.get('high', 0)
        if high_violations > 0:
            recommendations.append(f"🟠 Fix {high_violations} high severity issues in the next development cycle to improve code quality")
        
        medium_violations = violations_by_severity.get('medium', 0)
        if medium_violations > 0:
            recommendations.append(f"🟡 Plan to address {medium_violations} medium severity issues during regular maintenance")
        
        low_violations = violations_by_severity.get('low', 0)
        if low_violations > 0:
            recommendations.append(f"🔵 Consider addressing {low_violations} low severity issues for code perfection")
        
        if total_violations == 0:
            recommendations.append("🎉 Excellent! Code fully complies with the YAML specification. Maintain these high standards!")
        elif total_violations > 20:
            recommendations.append("📋 Consider implementing automated code quality checks in your CI/CD pipeline to catch issues early")
        
        if compliance_level in ['POOR', 'FAIR']:
            recommendations.append("🔄 Establish regular code review processes to maintain and improve code quality")
        
        recommendations_html = "".join([f"""
        <div style="display: flex; align-items: start; gap: 1rem; padding: 1rem; background: linear-gradient(135deg, #f0fdf4, #dcfce7); border-radius: 10px; margin-bottom: 0.75rem; border-left: 4px solid var(--success);">
            <div style="font-size: 1.25rem;">{rec.split(' ')[0]}</div>
            <div style="flex: 1;">{''.join(rec.split(' ')[1:])}</div>
        </div>
        """ for rec in recommendations])
        
        return f"""
        <div class="section">
            <h2 class="section-title"><i class="fas fa-lightbulb"></i> Recommendations & Action Plan</h2>
            <div style="background: linear-gradient(135deg, #f8fafc, #f1f5f9); padding: 2rem; border-radius: 12px; border: 1px solid var(--border);">
                <h4 style="margin-bottom: 1.5rem; color: var(--text); text-align: center;">Priority-Based Improvement Plan</h4>
                {recommendations_html}
            </div>
        </div>
        """