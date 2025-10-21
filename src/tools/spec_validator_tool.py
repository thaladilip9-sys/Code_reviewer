# spec_validator_tool.py
import os
import yaml
import json
import asyncio,time
from typing import Dict, List, Any, Optional
from langchain.agents import Tool
from langchain.schema import HumanMessage, SystemMessage
from src.utils.langchain_openai import OpenAILLM
from src.utils.logger import get_logger, logger_manager

# Get logger instance
logger = get_logger()
class SpecValidator:
    """
    Validates Python code against specification document using ONLY rules from YAML
    with step-by-step LLM analysis
    """
    
    def __init__(self, spec_file_path: str = "spec_docs\python_code_specification.yaml"):
        self.spec_file_path = spec_file_path
        self.specification = self._load_specification()
        self.llm = OpenAILLM().get_llm()
        self.streaming_llm = OpenAILLM().get_streaming_llm()
    
    def _load_specification(self) -> Dict[str, Any]:
        """Load specification document from YAML"""
        try:
            with open(self.spec_file_path, 'r', encoding='utf-8') as f:
                spec = yaml.safe_load(f)
                logger.info(f"✅ Loaded specification: {spec.get('specification', {}).get('name', 'Unknown')}")
                return spec
        except Exception as e:
            logger.error(f"❌ Failed to load specification: {e}")
            return {}
    
    def validate_code(self, state: Dict) -> Dict:
        """Validate code using rules from YAML specification - SYNC version"""
        logger.info("🧠 Starting pure YAML-driven specification validation...")
        
        try:
            files = state.get("files", [])
            if not files:
                return {"error": "No files to validate"}
            
            if not self.specification:
                return {"error": "No specification file loaded"}
            
            # Handle both async and sync contexts
            try:
                # Check if we're in an event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If event loop is running, use thread-based approach
                    return self._run_in_thread(files)
                else:
                    # If no running event loop, use asyncio.run()
                    return asyncio.run(self._run_pure_yaml_validation(files))
            except RuntimeError:
                # No event loop, use asyncio.run()
                return asyncio.run(self._run_pure_yaml_validation(files))
            
        except Exception as e:
            error_msg = f"Specification validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {"error": error_msg}
    
    def _run_in_thread(self, files: List[Dict]) -> Dict:
        """Run async validation in a separate thread"""
        import concurrent.futures
        
        def run_async():
            return asyncio.run(self._run_pure_yaml_validation(files))
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_async)
            return future.result()
    
    async def _run_pure_yaml_validation(self, files: List[Dict]) -> Dict:
        """Run validation using ONLY rules defined in YAML specification"""
        
        logger.info("=" * 70)
        logger.info("🔄 PURE YAML-DRIVEN VALIDATION")
        logger.info("=" * 70)
        
        validation_results = {
            "specification_used": self.specification.get('specification', {}),
            "validation_steps": {},
            "overall_metrics": {}
        }
        
        # Get all categories from YAML that have rules
        categories = self._get_categories_with_rules()
        logger.info(f"📊 Found {len(categories)} categories with rules in YAML")
        
        # Validate each category that has rules
        for category in categories:
            logger.info(f"\n🎯 Validating {category.replace('_', ' ').title()}...")
            category_results = await self._validate_yaml_category(files, category)
            validation_results["validation_steps"][category] = category_results
        
        # Calculate overall metrics
        validation_results["overall_metrics"] = self._calculate_overall_metrics(validation_results["validation_steps"])
        
        return validation_results
    
    def _get_categories_with_rules(self) -> List[str]:
        """Get all categories that have rules defined in YAML"""
        categories = []
        
        # Check coding_standards
        coding_standards = self.specification.get('coding_standards', {})
        if coding_standards.get('naming_conventions', {}).get('rules'):
            categories.append('naming_conventions')
        if coding_standards.get('code_structure', {}).get('rules'):
            categories.append('code_structure')
        if coding_standards.get('documentation', {}).get('rules'):
            categories.append('documentation')
        if coding_standards.get('error_handling', {}).get('rules'):
            categories.append('error_handling')
        if coding_standards.get('security', {}).get('rules'):
            categories.append('security')
        if coding_standards.get('performance', {}).get('rules'):
            categories.append('performance')
        
        return categories
    
    async def _validate_yaml_category(self, files: List[Dict], category: str) -> Dict:
        """Validate a specific category using ONLY rules from YAML"""
        
        # Get rules for this category directly from YAML
        category_rules = self._get_yaml_rules_for_category(category)
        logger.info(f"   📝 Applying {len(category_rules)} rules from YAML")
        
        if not category_rules:
            return {
                "yaml_rules": [],
                "json_analysis": {"error": f"No rules found for {category} in YAML"},
                "streaming_analysis": "skipped"
            }
        
        # JSON Analysis (non-streaming)
        json_task = asyncio.create_task(
            self._get_yaml_category_json_analysis(files, category, category_rules)
        )
        
        # Streaming Analysis - DISABLE printing during streaming
        streaming_task = asyncio.create_task(
            self._get_yaml_category_streaming_analysis_no_print(files, category, category_rules)
        )
        
        # Wait for both
        json_result, streaming_output = await asyncio.gather(
            json_task, streaming_task, return_exceptions=True
        )
        
        return {
            "yaml_rules": [rule.get('rule_id', 'unknown') for rule in category_rules],
            "json_analysis": json_result if not isinstance(json_result, Exception) else {"error": str(json_result)},
            "streaming_analysis": streaming_output if not isinstance(streaming_output, Exception) else {"error": str(streaming_output)}
        }
    

    async def _get_yaml_category_streaming_analysis_no_print(self, files: List[Dict], category: str, rules: List[Dict]) -> Dict:
        """Get streaming analysis WITHOUT printing - collect content only"""
        code_context = self._format_files_for_streaming(files)
        
        # Build human-readable rules summary from YAML
        rules_summary = self._build_yaml_rules_summary(rules)
        
        prompt = f"""
        Provide a HUMAN-READABLE analysis of {category.replace('_', ' ').title()} for this Python code.

        YAML SPECIFICATION RULES (YOU MUST USE ONLY THESE):
        {rules_summary}

        CODE:
        {code_context}

        Analyze how well the code follows our EXACT YAML specification rules.
        For each rule, explain:
        - What the rule requires
        - Whether the code complies
        - Specific examples from the code

        Use engaging, conversational language but stay strictly within the YAML rules.
        Do not add any additional rules or personal opinions.
        """
        
        messages = [
            SystemMessage(content=f"""You are an educational code reviewer analyzing against a YAML specification.
            You MUST only use the rules provided in the YAML.
            Provide a human-readable, step-by-step analysis in bullet points
            Make it engaging but strictly accurate to the specification."""),
            HumanMessage(content=prompt)
        ]
        
        logger.info(f"   💬 Running {category} analysis...")
        full_response = ""
        chunk_count = 0
        start_time = time.time()
        
        try:
            # Collect streaming response without printing
            async for chunk in self.streaming_llm.astream(messages):
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response += content
                chunk_count += 1
            
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"   ✅ {category} analysis completed - {chunk_count} chunks in {duration:.1f}s")
            logger.info(f"   📊 Generated {len(full_response):,} characters of analysis")
            logger.info(f"   📋 Applied {len(rules)} YAML rules")
            
            # Return the collected response as part of the result
            return {
                "streaming_content": full_response,
                "category": category,
                "rules_applied": [rule.get('rule_id', 'unknown') for rule in rules],
                "analysis_length": len(full_response),
                "chunk_count": chunk_count,
                "processing_time": duration
            }
            
        except Exception as e:
            logger.error(f"   ❌ {category} analysis failed: {e}")
            return {
                "error": f"Streaming analysis failed: {str(e)}",
                "category": category,
                "rules_applied": []
            }
    
    def _get_yaml_rules_for_category(self, category: str) -> List[Dict]:
        """Get rules for category directly from YAML structure"""
        coding_standards = self.specification.get('coding_standards', {})
        
        if category == 'naming_conventions':
            return coding_standards.get('naming_conventions', {}).get('rules', [])
        elif category == 'code_structure':
            return coding_standards.get('code_structure', {}).get('rules', [])
        elif category == 'documentation':
            return coding_standards.get('documentation', {}).get('rules', [])
        elif category == 'error_handling':
            return coding_standards.get('error_handling', {}).get('rules', [])
        elif category == 'security':
            return coding_standards.get('security', {}).get('rules', [])
        elif category == 'performance':
            return coding_standards.get('performance', {}).get('rules', [])
        else:
            return []
    
    async def _get_yaml_category_json_analysis(self, files: List[Dict], category: str, rules: List[Dict]) -> Dict:
        """Get structured JSON analysis using ONLY YAML rules"""
        code_context = self._format_files_for_analysis(files)
        
        # Build rules description directly from YAML
        rules_description = self._build_yaml_rules_description(rules)
        
        prompt = f"""
        Analyze the following Python code for {category.upper().replace('_', ' ')} compliance.

        YAML SPECIFICATION RULES:
        {rules_description}

        CODE TO ANALYZE:
        {code_context}

        Analyze the code against EXACTLY these rules from our YAML specification.
        Do not add any additional rules or assumptions.

        For each rule violation, provide:
        - Exact rule ID from YAML
        - File name and line number
        - Specific description of the violation
        - Suggested fix based on the rule

        Provide analysis in this EXACT JSON format:
        {{
            "category": "{category}",
            "rules_applied": {[rule.get('rule_id', 'unknown') for rule in rules]},
            "overall_compliance_score": 0-100,
            "files_analyzed": [],
            "detailed_violations": [
                {{
                    "yaml_rule_id": "RULE-ID-FROM-YAML",
                    "yaml_rule_name": "Rule Name from YAML",
                    "file": "filename.py",
                    "line": 10,
                    "violation_description": "specific description matching YAML rule",
                    "severity": "severity from YAML",
                    "suggestion": "fix based on YAML rule requirements"
                }}
            ],
            "compliant_files": ["list", "of", "files", "that", "follow", "all", "rules"],
            "summary": "overall assessment based ONLY on YAML specification rules"
        }}

        IMPORTANT: Only report violations that directly contradict the YAML rules provided.
        """
        
        messages = [
            SystemMessage(content=f"""You are a precise code validator that strictly follows YAML specifications.
            You MUST only use the rules provided in the YAML specification.
            Do not invent new rules or apply personal preferences.
            Be extremely specific and reference the exact YAML rules in your analysis."""),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return self._parse_json_response(response.content)
        except Exception as e:
            return {"error": f"LLM analysis failed: {str(e)}"}
    
    # async def _get_yaml_category_streaming_analysis(self, files: List[Dict], category: str, rules: List[Dict]) -> str:
    #     """Get streaming analysis using ONLY YAML rules"""
    #     code_context = self._format_files_for_streaming(files)
        
    #     # Build human-readable rules summary from YAML
    #     rules_summary = self._build_yaml_rules_summary(rules)
        
    #     prompt = f"""
    #     Provide a HUMAN-READABLE analysis of {category.replace('_', ' ').title()} for this Python code.

    #     YAML SPECIFICATION RULES (YOU MUST USE ONLY THESE):
    #     {rules_summary}

    #     CODE:
    #     {code_context}

    #     Analyze how well the code follows our EXACT YAML specification rules.
    #     For each rule, explain:
    #     - What the rule requires
    #     - Whether the code complies
    #     - Specific examples from the code

    #     Use engaging, conversational language but stay strictly within the YAML rules.
    #     Do not add any additional rules or personal opinions.
    #     """
        
    #     category_emojis = {
    #         'naming_conventions': '🎯',
    #         'code_structure': '🏗️', 
    #         'documentation': '📚',
    #         'error_handling': '🛡️',
    #         'security': '🔒',
    #         'performance': '⚡'
    #     }
        
    #     emoji = category_emojis.get(category, '📋')
        
    #     messages = [
    #         SystemMessage(content=f"""You are an educational code reviewer analyzing against a YAML specification.
    #         {emoji} You MUST only use the rules provided in the YAML.
    #         Make it engaging but strictly accurate to the specification."""),
    #         HumanMessage(content=prompt)
    #     ]
        
    #     logger.info(f"   💬 Streaming {category} analysis...")
    #     full_response = ""
        
    #     try:
    #         async for chunk in self.streaming_llm.astream(messages):
    #             content = chunk.content if hasattr(chunk, 'content') else str(chunk)
    #             logger.info(content, end="", flush=True)
    #             full_response += content
            
    #         logger.info(f"\n   ✅ {category} streaming completed")
    #         return full_response
    #     except Exception as e:
    #         logger.info(f"\n   ❌ {category} streaming failed: {e}")
    #         return f"Streaming analysis failed: {str(e)}"
    
    def _build_yaml_rules_description(self, rules: List[Dict]) -> str:
        """Build rules description directly from YAML data"""
        description = ""
        for rule in rules:
            description += f"\n--- Rule {rule.get('rule_id', 'unknown')} ---\n"
            description += f"Name: {rule.get('name', 'N/A')}\n"
            description += f"Description: {rule.get('description', 'N/A')}\n"
            description += f"Severity: {rule.get('severity', 'N/A')}\n"
            
            # Include all rule properties from YAML
            for key, value in rule.items():
                if key not in ['rule_id', 'name', 'description', 'severity']:
                    if isinstance(value, list):
                        description += f"{key}: {', '.join(map(str, value))}\n"
                    else:
                        description += f"{key}: {value}\n"
        
        return description
    
    def _build_yaml_rules_summary(self, rules: List[Dict]) -> str:
        """Build human-readable rules summary from YAML"""
        summary = ""
        for rule in rules:
            rule_id = rule.get('rule_id', 'unknown')
            rule_name = rule.get('name', 'Unnamed Rule')
            severity = rule.get('severity', 'unknown')
            description = rule.get('description', 'No description provided')
            
            summary += f"• {rule_id}: {rule_name} ({severity} severity)\n"
            summary += f"  {description}\n"
            
            # Add specific requirements
            if 'pattern' in rule:
                summary += f"  Pattern: {rule['pattern']}\n"
            if 'max_lines' in rule:
                summary += f"  Max Lines: {rule['max_lines']}\n"
            if 'required' in rule:
                summary += f"  Required: {rule['required']}\n"
        
        return summary
    
    def _format_files_for_analysis(self, files: List[Dict]) -> str:
        """Format files for detailed analysis"""
        formatted = ""
        for file in files:
            formatted += f"\n{'='*50}\n"
            formatted += f"FILE: {file.get('file_name', 'unknown')}\n"
            formatted += f"LANGUAGE: {file.get('language', 'unknown')}\n"
            code_content = file.get('code', '')
            if len(code_content) > 2000:
                formatted += f"CONTENT (first 2000 chars):\n```python\n{code_content[:2000]}\n...\n```\n"
            else:
                formatted += f"CONTENT:\n```python\n{code_content}\n```\n"
        return formatted
    
    def _format_files_for_streaming(self, files: List[Dict]) -> str:
        """Format files for streaming analysis"""
        formatted = f"Analyzing {len(files)} files:\n"
        for file in files:
            formatted += f"• {file.get('file_name', 'unknown')} ({len(file.get('code', ''))} chars)\n"
        return formatted
    
    def _parse_json_response(self, content: str) -> Dict:
        """Parse JSON response from LLM"""
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].strip()
                if json_str.startswith("json"):
                    json_str = json_str[4:].strip()
            else:
                json_str = content.strip()
            
            return json.loads(json_str)
        except Exception as e:
            return {"error": f"Failed to parse JSON: {e}", "raw_content": content[:500]}
    
    def _calculate_overall_metrics(self, validation_steps: Dict) -> Dict:
        """Calculate overall validation metrics based on YAML rules"""
        total_violations = 0
        total_rules_applied = 0
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for category, results in validation_steps.items():
            json_analysis = results.get("json_analysis", {})
            if isinstance(json_analysis, dict) and "detailed_violations" in json_analysis:
                violations = json_analysis["detailed_violations"]
                total_violations += len(violations)
                total_rules_applied += len(results.get("yaml_rules", []))
                
                for violation in violations:
                    severity = violation.get("severity", "low")
                    if severity in severity_counts:
                        severity_counts[severity] += 1
        
        overall_score = 100
        if total_rules_applied > 0:
            # Simple scoring: deduct points for violations
            violation_penalty = min(total_violations * 10, 100)
            overall_score = max(0, 100 - violation_penalty)
        
        return {
            "total_categories_validated": len(validation_steps),
            "total_yaml_rules_applied": total_rules_applied,
            "total_violations_found": total_violations,
            "violations_by_severity": severity_counts,
            "overall_compliance_score": overall_score,
            "compliance_level": self._get_compliance_level(overall_score)
        }
    
    def _get_compliance_level(self, score: float) -> str:
        """Get compliance level based on score"""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 75:
            return "GOOD"
        elif score >= 60:
            return "FAIR"
        else:
            return "POOR"

    def get_tool(self) -> Tool:
        """Convert to LangChain Tool"""
        return Tool(
            name="Pure YAML Specification Validator",
            func=self.validate_code,
            description="""Validates Python code against YAML specification document using ONLY rules from YAML.
Input: State with 'files' list containing code
Output: Detailed validation results based strictly on YAML specification rules
"""
        )

# Initialize the tool
# spec_validator_tool = PureYAMLSpecValidator().get_tool()