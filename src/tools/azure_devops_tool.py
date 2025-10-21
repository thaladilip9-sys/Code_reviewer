# src/tools/azure_devops_tool.py
from typing import Dict, Any, List
import os
import tempfile
import pathlib
from src.services.azure_devops_service import AzureDevOpsService, UserStory, CodeFile

class AzureDevOpsTool:
    def __init__(self):
        self.tool_name = "azure_devops_fetcher"
        self.description = "Fetches user stories and code content from Azure DevOps"
    
    def get_tool(self):
        return {
            "type": "function",
            "function": {
                "name": self.tool_name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "state": {
                            "type": "object",
                            "description": "Code review state"
                        }
                    },
                    "required": ["state"]
                }
            }
        }
    
    def func(self, state: Dict) -> Dict:
        """Main function to fetch Azure DevOps data and prepare for review"""
        try:
            if not state.get("azure_config"):
                return {
                    "error": "Azure DevOps configuration not provided",
                    "skipped": True
                }
            
            azure_config = state["azure_config"]
            iteration_path = state.get("iteration_path")

            # print("Azure config\n",azure_config)
            
            # Initialize Azure DevOps service
            azure_service = AzureDevOpsService(
                organization=azure_config.get("organization"),
                project=azure_config.get("project"),
                personal_access_token=azure_config.get("personal_access_token")
            )
            
            # Test connection first
            # print("🔗 Testing Azure DevOps connection...")
            # if not azure_service.test_connection():
            #     return {
            #         "error": "Failed to connect to Azure DevOps. Check organization, project, and PAT.",
            #         "skipped": True
            #     }
            
            # Get only user stories that have commits
            print("📋 Fetching user stories with commits from Azure DevOps...")
            user_stories = azure_service.get_user_stories_with_commits(iteration_path)
            
            if not user_stories:
                return {
                    "error": "No user stories with commits found",
                    "skipped": True
                }
            
            print(f"🎯 Found {len(user_stories)} user stories with commits")
            
            all_code_files = []
            all_requirements = []
            user_story_details = []
            
            # Limit to first 3 user stories to avoid timeout
            max_stories = 3
            stories_to_process = user_stories[:max_stories]
            
            if len(user_stories) > max_stories:
                print(f"⚠️ Processing first {max_stories} user stories to avoid timeout")
            
            for user_story in stories_to_process:
                print(f"\n🔍 Processing User Story: {user_story.title} (ID: {user_story.id})")
                
                # Get code files for user story (we already know it has commits)
                code_files = azure_service.get_all_code_files_for_user_story(user_story.id)
                
                if code_files:
                    all_code_files.extend(code_files)
                    
                    # Prepare requirements
                    requirements = azure_service.prepare_requirements_from_story(user_story)
                    all_requirements.append(requirements)
                    
                    user_story_details.append({
                        "id": user_story.id,
                        "title": user_story.title,
                        "description": user_story.description,
                        "state": user_story.state,
                        "file_count": len(code_files)
                    })
                    
                    print(f"✅ Extracted {len(code_files)} code files for user story {user_story.id}")
                    
                    # Show file names
                    for code_file in code_files[:5]:  # Show first 5 files
                        print(f"   📄 {code_file.file_path} ({code_file.language})")
                    
                    if len(code_files) > 5:
                        print(f"   ... and {len(code_files) - 5} more files")
                else:
                    # This shouldn't happen since we filtered stories with commits, but handle it
                    print(f"⚠️ No code files found for user story {user_story.id} (but it has commits)")
            
            if not all_code_files:
                return {
                    "error": "No code files found in user stories with commits",
                    "skipped": True
                }
            
            # Convert code files to the format expected by the code review agent
            files_data = self._prepare_files_data(all_code_files)
            
            # Update state with fetched data
            state["files"] = files_data
            state["azure_user_stories"] = user_story_details
            
            # Combine all requirements
            combined_requirements = self._combine_requirements(all_requirements)
            state["requirements"] = combined_requirements
            
            return {
                "success": True,
                "user_stories_count": len(user_stories),
                "processed_stories_count": len(stories_to_process),
                "files_count": len(all_code_files),
                "user_stories": user_story_details,
                "code_files_summary": {
                    "total_files": len(all_code_files),
                    "languages": self._get_language_summary(all_code_files)
                }
            }
            
        except Exception as e:
            return {
                "error": f"Azure DevOps fetch failed: {str(e)}",
                "skipped": True
            }
    
    def _prepare_files_data(self, code_files: List[CodeFile]) -> List[Dict]:
        """Convert CodeFile objects to the format expected by code review agent"""
        files_data = []
        
        for code_file in code_files:
            files_data.append({
                "file_name": code_file.file_name,
                "file_path": code_file.file_path,
                "language": code_file.language,
                "code": code_file.content,
                "azure_metadata": {
                    "commit_id": code_file.commit_id,
                    "repository": code_file.repository,
                    "original_path": code_file.file_path
                }
            })
        
        return files_data
    
    def _combine_requirements(self, all_requirements: List[Dict]) -> Dict:
        """Combine requirements from multiple user stories"""
        combined = {
            "user_stories": [],
            "acceptance_criteria": [],
            "functional_requirements": [],
            "security_requirements": [],
            "descriptions": [],
            "azure_story_ids": []
        }
        
        for req in all_requirements:
            combined["user_stories"].extend(req.get("user_stories", []))
            combined["acceptance_criteria"].extend(req.get("acceptance_criteria", []))
            combined["functional_requirements"].extend(req.get("functional_requirements", []))
            combined["security_requirements"].extend(req.get("security_requirements", []))
            combined["descriptions"].append(req.get("description", ""))
            combined["azure_story_ids"].append(req.get("azure_story_id"))
        
        # Remove duplicates
        for key in combined:
            if isinstance(combined[key], list) and key != "azure_story_ids" and key != "descriptions":
                combined[key] = list(set(combined[key]))
        
        return combined
    
    def _get_language_summary(self, code_files: List[CodeFile]) -> Dict:
        """Get summary of programming languages in code files"""
        language_count = {}
        for code_file in code_files:
            lang = code_file.language
            language_count[lang] = language_count.get(lang, 0) + 1
        
        return language_count