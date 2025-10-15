# deep_evaluator.py
from typing import Dict, List, Any
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
import json

class DeepEvaluator:
    """
    DeepEval integration using requirement alignment metric for code evaluation.
    """
    
    def __init__(self):
        self.metric = GEval(
            name="Requirement Alignment",
            criteria="""Evaluate how well the code aligns with the specified requirements. Consider:
1. Requirement coverage - how many requirements are implemented
2. Implementation accuracy - how correctly requirements are implemented  
3. Completeness - is the implementation complete for each requirement
4. Edge case handling - are requirement edge cases considered
5. Specification adherence - does it follow requirement specifications exactly""",
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            threshold=0.7
        )
    
    def deep_evaluate(self, state: Dict) -> Dict:
        """Perform evaluation using DeepEval requirement alignment metric"""
        print("🔬 Running DeepEval requirement alignment evaluation...")
        
        try:
            files = state.get("files", [])
            requirements = state.get("requirements", {})
            
            if not files:
                state["deep_evaluation"] = {
                    "error": "No code files available for evaluation"
                }
                return state
            
            # Evaluate each file
            file_evaluations = []
            for file in files:
                file_eval = self._evaluate_single_file(file, requirements)
                file_evaluations.append(file_eval)
            
            # Generate overall results
            state["deep_evaluation"] = {
                "file_evaluations": file_evaluations,
                "overall_score": self._calculate_overall_score(file_evaluations),
                "summary": self._generate_summary(file_evaluations),
                "recommendations": self._generate_recommendations(file_evaluations)
            }
            
            print("✅ DeepEval evaluation completed")
            
        except Exception as e:
            state["deep_evaluation"] = {
                "error": f"DeepEval evaluation failed: {str(e)}"
            }
            print(f"❌ DeepEval evaluation error: {e}")
        
        return state
    
    def _evaluate_single_file(self, file: Dict, requirements: Dict) -> Dict:
        """Evaluate a single file using requirement alignment metric"""
        file_name = file.get("file_name", "unknown")
        code_content = file.get("code", "")
        language = file.get("language", "unknown")
        
        # Create test case for the file
        test_case = LLMTestCase(
            input=f"Evaluate code file: {file_name}",
            actual_output=code_content,
            expected_output=self._create_expected_output(requirements, language),
            retrieval_context=[f"Language: {language}", f"Requirements: {json.dumps(requirements)}"]
        )
        
        # Evaluate with requirement alignment metric
        try:
            # Create a new instance of the metric for this evaluation
            metric = GEval(
                name="Requirement Alignment",
                criteria=self.metric.criteria,
                evaluation_params=self.metric.evaluation_params,
                threshold=self.metric.threshold
            )
            
            # Measure the metric
            metric.measure(test_case)
            
            metric_result = {
                "score": metric.score,
                "reasoning": metric.reason,
                "passed": metric.score >= metric.threshold
            }
            
        except Exception as e:
            metric_result = {
                "score": 0.0,
                "reasoning": f"Evaluation failed: {str(e)}",
                "passed": False
            }
        
        return {
            "file_name": file_name,
            "language": language,
            "metric": metric_result,
            "overall_score": metric_result["score"],
            "passed": metric_result["passed"]
        }
    
    def _create_expected_output(self, requirements: Dict, language: str) -> str:
        """Create expected output description based on requirements"""
        if not requirements:
            return f"Well-structured, correct {language} code following best practices"
        
        req_description = []
        for key, value in requirements.items():
            if isinstance(value, dict):
                desc = value.get('description', '')
                req_description.append(f"{key}: {desc}" if desc else key)
            else:
                req_description.append(f"{key}: {value}")
        
        return f"Code that implements: {', '.join(req_description)}"
    
    def _calculate_overall_score(self, file_evaluations: List[Dict]) -> float:
        """Calculate overall score across all files"""
        if not file_evaluations:
            return 0.0
        
        total_score = sum(file_eval["overall_score"] for file_eval in file_evaluations)
        return round(total_score / len(file_evaluations), 2)
    
    def _generate_summary(self, file_evaluations: List[Dict]) -> str:
        """Generate evaluation summary"""
        if not file_evaluations:
            return "No evaluation data available"
        
        overall_score = self._calculate_overall_score(file_evaluations)
        passed_files = sum(1 for file_eval in file_evaluations if file_eval.get("passed", False))
        total_files = len(file_evaluations)
        
        summary = f"""
📊 DeepEval Requirement Alignment Summary
────────────────────────────────────────

Overall Score: {overall_score:.2f}/1.0
Files Passed: {passed_files}/{total_files}
Threshold: {self.metric.threshold}

File Scores:
"""
        
        for file_eval in file_evaluations:
            file_name = file_eval["file_name"]
            score = file_eval["overall_score"]
            status = "✅" if file_eval["passed"] else "❌"
            summary += f"  {file_name}: {score:.2f} {status}\n"
        
        return summary
    
    def _generate_recommendations(self, file_evaluations: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for file_eval in file_evaluations:
            if not file_eval["passed"]:
                file_name = file_eval["file_name"]
                score = file_eval["overall_score"]
                reasoning = file_eval["metric"]["reasoning"]
                
                # Extract key issues from reasoning
                if "missing" in reasoning.lower() or "not implemented" in reasoning.lower():
                    recommendations.append(f"Add missing requirements in {file_name}")
                elif "incorrect" in reasoning.lower() or "wrong" in reasoning.lower():
                    recommendations.append(f"Fix incorrect implementation in {file_name}")
                elif "incomplete" in reasoning.lower():
                    recommendations.append(f"Complete partial implementation in {file_name}")
                else:
                    recommendations.append(f"Improve requirement alignment in {file_name} (score: {score:.2f})")
        
        if not recommendations:
            recommendations.append("All files meet requirement alignment threshold - good job!")
        
        return recommendations[:5]
    
    def get_tool(self):
        """Get LangChain tool for integration"""
        from langchain.agents import Tool
        
        return Tool(
            name="Requirement Alignment Evaluator",
            func=self.deep_evaluate,
            description="Evaluate how well code aligns with specified requirements using DeepEval"
        )