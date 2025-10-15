# main.py
import asyncio
import os,warnings
from src.agents.code_reviewer_agent import create_code_review_agent
# Add at the very beginning of main.py
# Suppress the specific event loop warning

import asyncio
# asyncio.get_event_loop().set_debug(False)  # Disable asyncio debug mode
async def main():
    """Example usage of the CodeReviewerAgent with directory scanning"""
    
    # Create the code review agent
    agent = await create_code_review_agent()
    
    
    # Create a requirements file to test requirement validation
    requirements = {
        "user_stories": [
            "As a user, I want to register with email and password",
            "As a user, I want to login with my credentials",
            "As a user, I want to reset my password if forgotten",
            "As an admin, I want to manage user accounts"
        ],
        "functional_requirements": [
            "Secure user registration with validation",
            "JWT-based authentication system",
            "Password hashing with strong algorithm",
            "Input validation to prevent SQL injection",
            "Proper error handling and logging",
            "Secure configuration management"
        ],
        "security_requirements": [
            "No hardcoded credentials",
            "Input sanitization for all user inputs",
            "Secure password storage",
            "Protection against common vulnerabilities (SQLi, XSS, etc.)",
            "Proper access controls"
        ]
    }
    
    print("🚀 Starting comprehensive code review...")
    print("=" * 60)
    sample_dir=r"sample_code_repo"
    # # Example 1: Review entire directory without requirements
    # print("\n1. 📁 Reviewing directory without requirements...")
    # results_dir = await agent.review_directory(sample_dir)
    
    print("\n" + "=" * 60)
    
    # Example 2: Review directory with requirements
    print("\n1. 📁 Reviewing directory WITH requirements...")
    results_with_reqs = await agent.review_directory(sample_dir, requirements)
    
    print("\n" + "=" * 60)

def Sample():
    print("AAAAAAAAA")
    
if __name__ == "__main__":
    asyncio.run(main())
    Sample()