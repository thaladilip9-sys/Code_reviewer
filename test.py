# debug_deep_evaluator.py
import sys
import os
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from dotenv import load_dotenv
load_dotenv('./env/.env.local')
def test_deep_evaluator():
    """Test the DeepEvaluator tool separately"""
    try:
        # Import the tool
        from src.tools.deep_evaluator_tool import DeepEvaluator
        
        print("🚀 Initializing DeepEvaluator...")
        evaluator = DeepEvaluator()
        
        # Create test state
        test_state = {
            "files": [
                {
                    "file_name": "calculator.py",
                    "language": "python", 
                    "code": """
class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, x, y):
        return x * y
    
    def divide(self, numerator, denominator):
        if denominator == 0:
            raise ValueError("Cannot divide by zero")
        return numerator / denominator
"""
                }
            ],
            "requirements": {
                "basic_operations": "Implement basic arithmetic operations",
                "error_handling": "Handle division by zero errors",
                "class_structure": "Use object-oriented design with Calculator class"
            }
        }
        
        print("🔬 Running DeepEvaluator...")
        result = evaluator.deep_evaluate(test_state)
        
        print("✅ DeepEvaluator completed successfully!")
        print("\n📊 RESULTS:")
        print(json.dumps(result, indent=2, default=str))
        
        # Print summary
        if "deep_evaluation" in result:
            de_result = result["deep_evaluation"]
            if "error" in de_result:
                print(f"❌ Error: {de_result['error']}")
            else:
                print(f"\n📈 Overall Score: {de_result.get('overall_score', 'N/A')}")
                print(f"📋 Summary: {de_result.get('summary', 'No summary')}")
                print(f"💡 Recommendations: {de_result.get('recommendations', [])}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the file structure is correct:")
        print("project/")
        print("├── src/")
        print("│   └── tools/")
        print("│       └── deep_evaluator_tool.py")
        print("└── debug_deep_evaluator.py")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deep_evaluator()