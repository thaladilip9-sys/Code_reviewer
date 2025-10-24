import json
import openai

def convert_logs_to_json(log_file_path, api_key):
    # Read log file
    with open(log_file_path, 'r') as file:
        logs = file.read()
    
    # Set up API
    openai.api_key = api_key
    
    # Create prompt
    prompt = f"""
    Convert these logs into JSON step by step. Follow the exact sequence in the logs:
    
    {logs}
    
    Create JSON with this structure:
    {{
        "steps": [
            {{
                "step_number": 1,
                "action": "what happened",
                "function": "function name", 
                "parameters": "parameters used",
                "purpose": "why this was done"
            }}
        ],
        "current_status": "what is happening now",
        "next_actions": ["what should happen next"]
    }}
    """
    
    # Call LLM
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You convert logs to JSON. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    
    # Get result
    result = response.choices[0].message.content.strip()
    
    # Clean JSON
    if "```json" in result:
        result = result.split("```json")[1].split("```")[0].strip()
    elif "```" in result:
        result = result.split("```")[1].split("```")[0].strip()
    
    return json.loads(result)

# Usage
if __name__ == "__main__":
    api_key = "your-api-key-here"
    log_file = "agent_logs.txt"
    
    result = convert_logs_to_json(log_file, api_key)
    
    # Save result
    with open("output.json", "w") as f:
        json.dump(result, f, indent=2)
    
    print("JSON saved to output.json")
    print(json.dumps(result, indent=2))