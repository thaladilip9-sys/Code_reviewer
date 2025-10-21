# main.py
import asyncio
import os
from src.agents.code_reviewer_agent import create_code_review_agent

async def main():
    """Example usage of the CodeReviewerAgent with Azure DevOps integration"""
    
    # Create the code review agent
    agent = await create_code_review_agent()
    
    organization=os.getenv("AZURE_DEVOPS_ORG")
    project=os.getenv("AZURE_DEVOPS_PROJECT")
    personal_access_token=os.getenv("AZURE_DEVOPS_TOKEN")
    # Azure DevOps configuration - UPDATE THESE VALUES


    azure_config = {
        "organization": organization,  # Your organization
        "project": project,       # Your project name
        "personal_access_token": personal_access_token # Your Personal Access Token
    }
    
    # Optional: Specific iteration (set to None to get all iterations)
    iteration_path = "aimetlab2"  # Or "Sprint 1", "Iteration 1", etc.
    
    print("🚀 Starting Azure DevOps Code Review...")
    print("=" * 60)
    
    try:
        # Review using Azure DevOps
        results = await agent.review_azure_devops(
            azure_config=azure_config,
            iteration_path=iteration_path
        )
        
        print("\n" + "=" * 60)
        print("✅ Azure DevOps Code Review Completed!")
        
        # Print summary
        if results.get('azure_data', {}).get('success'):
            azure_data = results['azure_data']
            print(f"\n📊 Summary:")
            print(f"   User Stories with commits: {azure_data.get('user_stories_count', 0)}")
            print(f"   Processed: {azure_data.get('processed_stories_count', 0)}")
            print(f"   Code Files: {azure_data.get('files_count', 0)}")
            
        elif results.get('error'):
            print(f"❌ Error: {results['error']}")
        else:
            print("ℹ️ Review completed with partial results")
            
    except Exception as e:
        print(f"❌ Main execution error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())