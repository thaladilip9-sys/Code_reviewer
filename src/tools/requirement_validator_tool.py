# requirement_validator.py
import os
import json
import time
import re
import asyncio
from typing import Dict, List, Any
from langchain.agents import Tool
from langchain.schema import HumanMessage, SystemMessage
from src.utils.langchain_openai import OpenAILLM
from datetime import datetime

class RequirementValidator:
    """
    Validates code implementation against requirements with async streaming output.
    Provides separate JSON creation and beautified streaming.
    """
    
    def __init__(self):
        # Use streaming LLM for real-time output
        self.llm = OpenAILLM().get_streaming_llm()
        self.non_streaming_llm = OpenAILLM().get_non_streaming_llm()
    
    def validate_requirements(self, state: Dict) -> Dict:
        """Validate code implementation - sync wrapper for async method"""
        print("🔍 Starting comprehensive requirements validation...\n")
        
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If event loop is running, use thread-based approach
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(self._run_async_in_thread, state)
                        return future.result()
                else:
                    # If no running event loop, use asyncio.run()
                    return asyncio.run(self._async_validate_requirements(state))
            except RuntimeError:
                # No event loop, use asyncio.run()
                return asyncio.run(self._async_validate_requirements(state))
                
        except Exception as e:
            error_msg = f"Requirement validation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "timestamp": str(datetime.now())
            }
    
    def _run_async_in_thread(self, state: Dict) -> Dict:
        """Run async function in a separate thread"""
        return asyncio.run(self._async_validate_requirements(state))
    
    async def _async_validate_requirements(self, state: Dict) -> Dict:
        """Async implementation of requirement validation"""
        try:
            # Extract requirements and code from state
            requirements = state.get("requirements", {})
            files = state.get("files", [])
            
            if not requirements:
                print("ℹ️ No requirements provided - skipping validation")
                return {
                    "skipped": True,
                    "reason": "No requirements provided for validation",
                    "timestamp": str(datetime.now())
                }
            
            if not files:
                print("❌ No code files available for analysis")
                return {
                    "error": "No code files available for requirement validation",
                    "timestamp": str(datetime.now())
                }
            
            print(f"📋 Found {len(requirements)} requirements and {len(files)} code files\n")
            
            # Perform async streaming analysis
            analysis_result = await self._async_streaming_analysis(requirements, files)
            
            # Add metadata
            analysis_result["timestamp"] = str(datetime.now())
            analysis_result["files_analyzed"] = len(files)
            analysis_result["requirements_analyzed"] = len(requirements)
            
            print("\n🎯 Requirement validation completed successfully!")
            return analysis_result
            
        except Exception as e:
            error_msg = f"Requirement validation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "error": error_msg,
                "timestamp": str(datetime.now())
            }
    
    async def _async_streaming_analysis(self, requirements: Dict, files: List[Dict]) -> Dict:
        """Perform async analysis with separate JSON creation and beautified streaming"""
        
        print("=" * 70)
        print("🔄 Performing Async Requirements Analysis")
        print("=" * 70)
        
        # Step 1: Create structured JSON analysis (non-streaming)
        print("\n📊 Step 1: Creating structured JSON analysis...")
        json_analysis_task = asyncio.create_task(
            self._create_json_analysis(requirements, files)
        )
        
        # Step 2: Run beautified streaming analysis concurrently
        print("🎨 Step 2: Starting beautified streaming analysis...")
        streaming_task = asyncio.create_task(
            self._beautified_streaming_analysis(requirements, files)
        )
        
        # Wait for both tasks to complete
        json_result, streaming_output = await asyncio.gather(
            json_analysis_task,
            streaming_task,
            return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(json_result, Exception):
            print(f"❌ JSON analysis failed: {json_result}")
            return self._create_fallback_structure()
        
        if isinstance(streaming_output, Exception):
            print(f"⚠️ Streaming analysis had issues: {streaming_output}")
        
        print("\n✅ Both JSON and streaming analysis completed!")
        
        # Display comprehensive summary
        self._display_comprehensive_summary(json_result)
        
        return json_result
    
    async def _create_json_analysis(self, requirements: Dict, files: List[Dict]) -> Dict:
        """Create structured JSON analysis using non-streaming LLM"""
        try:
            prompt = self._create_json_analysis_prompt(requirements, files)
            
            messages = [
                SystemMessage(content="""You are a meticulous requirements analyst. 
                Create a structured JSON analysis with specific code references.
                Your output MUST follow the exact JSON format provided.
                Be precise and evidence-based."""),
                HumanMessage(content=prompt)
            ]
            
            print("   🧠 Generating structured JSON analysis...")
            response = await self.non_streaming_llm.ainvoke(messages)
            
            # Parse the JSON response
            result = self._parse_json_response(response.content)
            print("   ✅ JSON analysis completed successfully")
            return result
            
        except Exception as e:
            print(f"   ❌ JSON analysis failed: {e}")
            raise e
    
    async def _beautified_streaming_analysis(self, requirements: Dict, files: List[Dict]) -> str:
        """Perform beautified streaming analysis with human-readable output"""
        try:
            prompt = self._create_beautified_prompt(requirements, files)
            
            messages = [
                SystemMessage(content="""You are an expert software requirements analyst. 
                Provide a human-readable, step-by-step analysis of how well the code implements requirements.
                Use clear, engaging language with emojis and bullet points.
                Focus on telling a story about the implementation status."""),
                HumanMessage(content=prompt)
            ]
            
            print("   " + "=" * 50)
            
            full_response = ""
            async for chunk in self.llm.astream(messages):
                # time.sleep(0.2)
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                print(content, end="", flush=True)
                
                full_response += content
                # time.sleep(0.1)
            
            print("\n   " + "=" * 50)
            
            return full_response
            
        except Exception as e:
            print(f"   ⚠️ Streaming analysis interrupted: {e}")
            return ""
    
    def _create_json_analysis_prompt(self, requirements: Dict, files: List[Dict]) -> str:
        """Create prompt for structured JSON analysis"""
        return f"""
        Create a comprehensive JSON analysis of requirement implementation.

        REQUIREMENTS:
        {json.dumps(requirements, indent=2)}

        CODE FILES:
        {self._format_files_for_json(files)}

        OUTPUT FORMAT (STRICT JSON) ***DON'T CHANGE ANY KEYS***:
        {{
            "comprehensive_analysis": {{
                "overall_alignment_scores": {{
                    "user_stories": {{
                        "total": 0,
                        "implemented": 0,
                        "not_implemented": 0,
                        "average_confidence_score": 0.0
                    }},
                    "functional_requirements": {{
                        "total": 0,
                        "implemented": 0,
                        "not_implemented": 0,
                        "average_confidence_score": 0.0
                    }},
                    "security_requirements": {{
                        "total": 0,
                        "implemented": 0,
                        "not_implemented": 0,
                        "average_confidence_score": 0.0
                    }},
                    "non_functional_requirements": {{
                        "total": 0,
                        "implemented": 0,
                        "not_implemented": 0,
                        "average_confidence_score": 0.0
                    }}
                }},
                "requirement_details": {{
                    "user_stories": [
                        {{
                            "id": "US-1",
                            "description": "User story description",
                            "status": "Fully Implemented",
                            "confidence_score": 95.0,
                            "implemented_files": ["file1.py", "file2.py"],
                            "code_evidence": "Specific functions and line numbers",
                            "gaps": "None or specific gaps"
                        }}
                    ],
                    "functional_requirements": [],
                    "security_requirements": [],
                    "non_functional_requirements": []
                }},
                "file_analysis": {{
                    "file1.py": {{
                        "requirements_covered": ["US-1", "FR-1"],
                        "coverage_percentage": 85.0,
                        "implementation_quality": "Good",
                        "issues_found": []
                    }}
                }},
                "executive_summary": "High-level summary of findings and critical gaps",
                "actionable_improvement_plans": {{
                    "short_term": "Immediate actions (1-2 weeks)",
                    "medium_term": "Next phase actions (3-4 weeks)", 
                    "long_term": "Strategic improvements (1-2 months)"
                }}
            }},
            "alignment_analysis": {{
                "overall_alignment_score": 0.85,
                "coverage_metrics": {{
                    "total_requirements": 15,
                    "fully_covered": 8,
                    "partially_covered": 4,
                    "missing": 3,
                    "coverage_percentage": 80.0
                }}
            }}
        }}

        Be precise and evidence-based. Only report what you can verify in the code.
        """
    
    def _create_beautified_prompt(self, requirements: Dict, files: List[Dict]) -> str:
        """Create prompt for beautified streaming analysis"""
        return f"""
        Provide a beautiful, human-readable analysis of how well the code implements the requirements.

        REQUIREMENTS TO ANALYZE:
        {json.dumps(requirements, indent=2)}

        CODE FILES:
        {len(files)} files with {sum(len(f.get('code', '')) for f in files)} total characters

        ANALYSIS FORMAT:
        🎯 EXECUTIVE OVERVIEW
        - Overall implementation status
        - Key successes and gaps

        📊 REQUIREMENT BREAKDOWN
        - User Stories: ✅/❌ status with confidence
        - Functional Requirements: ✅/❌ status  
        - Security Requirements: ✅/❌ status
        - Non-Functional Requirements: ✅/❌ status

        🔍 KEY FINDINGS
        - What's working well
        - Critical gaps identified
        - Code quality observations

        💡 RECOMMENDATIONS
        - Immediate actions needed
        - Strategic improvements

        Use engaging language, emojis, and make it easy to understand.
        Focus on telling the story of the implementation journey.
        """
    
    def _format_files_for_json(self, files: List[Dict]) -> str:
        """Format files for JSON analysis"""
        formatted = []
        for file in files:
            file_info = {
                "file_name": file.get('file_name', 'unknown'),
                "language": file.get('language', 'unknown'),
                "size": len(file.get('code', '')),
                "content_preview": file.get('code', '')[:1000] + "..." if len(file.get('code', '')) > 1000 else file.get('code', '')
            }
            formatted.append(file_info)
        return json.dumps(formatted, indent=2)
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON response from LLM"""
        try:
            # Extract JSON from response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
                if json_str.startswith("json"):
                    json_str = json_str[4:].strip()
            else:
                json_str = content.strip()
            
            result = json.loads(json_str)
            return self._validate_json_structure(result)
            
        except Exception as e:
            print(f"   ⚠️ JSON parsing failed: {e}")
            return self._create_fallback_structure()
    
    def _validate_json_structure(self, result: Dict) -> Dict:
        """Validate and enhance JSON structure"""
        # Ensure all required fields exist
        if "comprehensive_analysis" not in result:
            result["comprehensive_analysis"] = {}
        
        comp_analysis = result["comprehensive_analysis"]
        
        # Ensure required sections
        required_sections = {
            "overall_alignment_scores": {
                "user_stories": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                "functional_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                "security_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                "non_functional_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0}
            },
            "requirement_details": {
                "user_stories": [],
                "functional_requirements": [],
                "security_requirements": [],
                "non_functional_requirements": []
            },
            "file_analysis": {},
            "executive_summary": "Analysis completed",
            "actionable_improvement_plans": {}
        }
        
        for section, default in required_sections.items():
            if section not in comp_analysis:
                comp_analysis[section] = default
        
        if "alignment_analysis" not in result:
            result["alignment_analysis"] = {
                "overall_alignment_score": 0,
                "coverage_metrics": {
                    "total_requirements": 0,
                    "fully_covered": 0,
                    "partially_covered": 0,
                    "missing": 0,
                    "coverage_percentage": 0
                }
            }
        
        return result
    
    def _create_fallback_structure(self) -> Dict:
        """Create fallback structure"""
        return {
            "comprehensive_analysis": {
                "overall_alignment_scores": {
                    "user_stories": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                    "functional_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                    "security_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0},
                    "non_functional_requirements": {"total": 0, "implemented": 0, "not_implemented": 0, "average_confidence_score": 0}
                },
                "requirement_details": {
                    "user_stories": [],
                    "functional_requirements": [],
                    "security_requirements": [],
                    "non_functional_requirements": []
                },
                "file_analysis": {},
                "executive_summary": "Analysis completed with errors",
                "actionable_improvement_plans": {}
            },
            "alignment_analysis": {
                "overall_alignment_score": 0,
                "coverage_metrics": {
                    "total_requirements": 0,
                    "fully_covered": 0,
                    "partially_covered": 0,
                    "missing": 0,
                    "coverage_percentage": 0
                }
            },
            "parse_error": True
        }
    
    def _display_comprehensive_summary(self, result: Dict):
        """Display comprehensive analysis summary"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE ANALYSIS SUMMARY")
        print("=" * 70)
        
        comp_analysis = result.get("comprehensive_analysis", {})
        alignment_scores = comp_analysis.get("overall_alignment_scores", {})
        
        # Display implementation metrics
        print("\n🎯 IMPLEMENTATION METRICS:")
        for category, data in alignment_scores.items():
            if isinstance(data, dict):
                total = data.get("total", 0)
                implemented = data.get("implemented", 0)
                confidence = data.get("average_confidence_score", 0)
                
                if total > 0:
                    category_name = category.replace('_', ' ').title()
                    implementation_rate = (implemented / total) * 100
                    print(f"   📈 {category_name}: {implementation_rate:.1f}% implemented")
                    print(f"      ✅ {implemented}/{total} requirements")
                    print(f"      🎯 {confidence:.1f}% confidence")
        
        # Overall score
        overall_score = result.get("alignment_analysis", {}).get("overall_alignment_score", 0) * 100
        print(f"\n🏆 OVERALL ALIGNMENT: {overall_score:.1f}%")
        
        # Executive summary
        exec_summary = comp_analysis.get("executive_summary", "No summary available")
        print(f"\n📋 EXECUTIVE SUMMARY:\n   {exec_summary}")
        
        print("=" * 70)

    def get_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="Requirement Validator",
            func=self.validate_requirements,  # Use the sync wrapper
            description="""Validates code implementation against requirements with async streaming output.
Provides both structured JSON and beautified human-readable analysis.
Input: State with 'requirements' dict and 'files' list
Output: Comprehensive analysis with coverage metrics and recommendations
"""
        )