# example_usage.py
import asyncio
from src.agents.code_reviewer_agent import CodeReviewerAgent

async def main():
    reviewer = CodeReviewerAgent()
    
    # # 1. Review a single file
    # print("=== Reviewing single file ===")
    # result = await reviewer.review_files(["/path/to/your/file.py"])
    # print_result(result)
    
    # # 2. Review multiple files
    # print("\n=== Reviewing multiple files ===")
    # result = await reviewer.review_files([
    #     "/path/to/file1.py",
    #     "/path/to/file2.java",
    #     "/path/to/file3.js"
    # ])
    # print_result(result)
    
    # 3. Review entire directory
    print("\n=== Reviewing directory ===")
    result = await reviewer.review_directory(r"./sample_code_repo_py")
    print_result(result)
    
    # 4. Review code string directly
#     print("\n=== Reviewing code string ===")
#     code = """
# def calculate_sum(a, b):
#     return a + b
#     """
#     result = await reviewer.review_code(code=code)
#     print_result(result)

def print_result(result):
    """Helper function to print results"""
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        standards = result.get("standards_result", {})
        files = standards.get("files", [])
        print(f"Analyzed {len(files)} files")
        
        for file_result in files:
            print(f"\n📁 {file_result['file_name']} ({file_result['language']})")
            for analysis in file_result.get('analysis', []):
                print(f"  🔧 {analysis['tool']}:")
                print(f"     {analysis['result']}")

if __name__ == "__main__":
    asyncio.run(main())