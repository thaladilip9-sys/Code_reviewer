import json
import openai  # or your preferred LLM client
from typing import Dict, Any, List

class LLMJsonCreator:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM JSON creator
        
        Args:
            api_key: Your LLM API key
            model: The model to use for generation
        """
        self.api_key = api_key
        self.model = model
        # Initialize your LLM client here
        # openai.api_key = api_key  # for OpenAI
        
    def create_task_creation_prompt(self, agent_logs: str) -> str:
        """
        Create prompt for generating task creation JSON
        """
        prompt = f"""
        Based on the following agent logs about creating tasks for an Epic, generate a structured JSON response.

        AGENT LOGS:
        {agent_logs}

        Please create a JSON object with the following structure:

        {{
            "operation": "create_tasks",
            "epic_id": 3,
            "epic_title": "Parabank Authentication and Navigation",
            "new_tasks": [
                {{
                    "title": "task_title",
                    "description": "detailed_description",
                    "acceptance_criteria": ["criterion1", "criterion2", ...],
                    "estimate": "estimate_in_hours",
                    "type": "Task",
                    "tags": ["tag1", "tag2"]
                }}
            ],
            "rationale": "explanation_of_why_these_tasks_are_needed"
        }}

        Requirements for the new tasks:
        1. "Create Unit Tests for Login Functionality"
        2. "Document User Authentication Process" 
        3. "Conduct Security Review for Authentication Module"

        Provide realistic descriptions, acceptance criteria, and estimates for each task.
        """
        return prompt
    
    def create_work_item_batch_prompt(self, work_item_ids: List[int]) -> str:
        """
        Create prompt for generating work item batch JSON
        """
        prompt = f"""
        Based on the work item IDs: {work_item_ids}, create a JSON structure for batch processing.

        Generate a JSON object with the following structure:

        {{
            "operation": "get_work_items_batch",
            "work_item_ids": {work_item_ids},
            "fields": [
                "System.Id",
                "System.Title", 
                "System.State",
                "System.AssignedTo",
                "Microsoft.VSTS.Scheduling.Effort"
            ],
            "include_relations": true
        }}
        """
        return prompt
    
    def create_epic_analysis_prompt(self, epic_data: Dict[str, Any]) -> str:
        """
        Create prompt for generating epic analysis JSON
        """
        prompt = f"""
        Analyze the following epic data and create a structured breakdown:

        EPIC DATA:
        {json.dumps(epic_data, indent=2)}

        Generate a JSON analysis with this structure:

        {{
            "epic_analysis": {{
                "current_coverage": {{
                    "development": "percentage_or_status",
                    "testing": "percentage_or_status", 
                    "documentation": "percentage_or_status",
                    "security": "percentage_or_status"
                }},
                "missing_components": ["component1", "component2", ...],
                "recommended_tasks": [
                    {{
                        "priority": "high|medium|low",
                        "task_type": "development|testing|documentation|security",
                        "description": "task_description",
                        "estimated_effort": "estimate"
                    }}
                ],
                "risk_assessment": {{
                    "level": "high|medium|low",
                    "concerns": ["concern1", "concern2"]
                }}
            }}
        }}
        """
        return prompt
    
    def call_llm(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Make the actual LLM call and parse JSON response
        """
        try:
            # Example using OpenAI (adjust for your LLM provider)
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates structured JSON responses. Always return valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response if it's wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response_text}")
            return {"error": "Failed to parse JSON response"}
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {"error": str(e)}
    
    def generate_task_creation_json(self, agent_logs: str) -> Dict[str, Any]:
        """Generate JSON for task creation operation"""
        prompt = self.create_task_creation_prompt(agent_logs)
        return self.call_llm(prompt)
    
    def generate_batch_operation_json(self, work_item_ids: List[int]) -> Dict[str, Any]:
        """Generate JSON for batch work item operation"""
        prompt = self.create_work_item_batch_prompt(work_item_ids)
        return self.call_llm(prompt)
    
    def generate_epic_analysis_json(self, epic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON for epic analysis"""
        prompt = self.create_epic_analysis_prompt(epic_data)
        return self.call_llm(prompt)

# Example usage
def main():
    # Your agent logs content
    agent_logs_content = """
    Agent action: 
    Invoking: `human_input` with `{'operation_details': "I want to create new tasks under the Epic 'Parabank Authentication and Navigation' to cover unit testing, documentation, and security review. These tasks will ensure comprehensive coverage of the Epic's objectives. The tasks will be titled 'Create Unit Tests for Login Functionality', 'Document User Authentication Process', and 'Conduct Security Review for Authentication Module'. Each task will include detailed descriptions, acceptance criteria, and estimates. This step is necessary to ensure all aspects of the Epic are addressed and managed effectively. Do you approve this action?"}`
    """
    
    # Initialize the LLM JSON creator
    llm_creator = LLMJsonCreator(api_key="your-api-key-here")
    
    # Generate task creation JSON
    task_json = llm_creator.generate_task_creation_json(agent_logs_content)
    print("Task Creation JSON:")
    print(json.dumps(task_json, indent=2))
    
    # Generate batch operation JSON
    work_item_ids = [28, 29, 27]
    batch_json = llm_creator.generate_batch_operation_json(work_item_ids)
    print("\nBatch Operation JSON:")
    print(json.dumps(batch_json, indent=2))
    
    # Example epic data for analysis
    epic_data = {
        "id": 3,
        "title": "Parabank Authentication and Navigation",
        "existing_tasks": [
            "Handle Login Error Scenarios",
            "Develop Registration Page Navigation", 
            "Implement Login Functionality"
        ],
        "description": "Epic for authentication and navigation features"
    }
    
    # Generate epic analysis JSON
    analysis_json = llm_creator.generate_epic_analysis_json(epic_data)
    print("\nEpic Analysis JSON:")
    print(json.dumps(analysis_json, indent=2))

if __name__ == "__main__":
    main()