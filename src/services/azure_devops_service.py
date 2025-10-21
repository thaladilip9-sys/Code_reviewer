# src/services/azure_devops_service.py
import requests
import os
import json
import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass
import pathlib
import base64
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v7_0.work_item_tracking.models import Wiql


@dataclass
class UserStory:
    id: int
    title: str
    description: str
    state: str
    acceptance_criteria: str
    assigned_to: str

@dataclass
class Commit:
    commit_id: str
    message: str
    author: str
    date: str
    repository: str

@dataclass
class CodeFile:
    file_path: str
    file_name: str
    content: str
    language: str
    commit_id: str
    repository: str

class AzureDevOpsService:
    def __init__(self, organization: str, project: str, personal_access_token: str):
        self.organization = organization
        self.project = project
        self.personal_access_token = personal_access_token
        self.base_url = f"https://dev.azure.com/{organization}"
        
        # Use Azure DevOps SDK for authentication
        credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=self.base_url, creds=credentials)
        self.wit_client = self.connection.clients.get_work_item_tracking_client()
        self.git_client = self.connection.clients.get_git_client()
        
        # Also keep requests session for REST API calls
        self.session = requests.Session()
        self.session.auth = ('', personal_access_token)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })

    def get_user_stories(self, iteration_path: Optional[str] = None) -> List[UserStory]:
        """Fetch user stories from Azure DevOps"""
        try:
            
            # Build WIQL query using the SDK
            base_query = f"""
            SELECT [System.Id], [System.Title], [System.State], [System.Description],
                   [Microsoft.VSTS.Common.AcceptanceCriteria], [System.AssignedTo]
            FROM WorkItems 
            WHERE [System.WorkItemType] = 'User Story' 
            AND [System.State] <> 'Closed'
            """

            if iteration_path:
                base_query += f" AND [System.IterationPath] = '{iteration_path}'"

            print(f"🔍 Executing WIQL query...")
            
            wiql = Wiql(query=base_query)
            query_results = self.wit_client.query_by_wiql(wiql)
            
            if not query_results.work_items:
                print("ℹ️ No work items found with the query")
                return []

            work_item_ids = [wi.id for wi in query_results.work_items]
            print(f"📋 Found {len(work_item_ids)} work items")
            
            # Get detailed work item information
            work_items = self.wit_client.get_work_items(
                ids=work_item_ids,
                expand='All'
            )

            user_stories = []
            for item in work_items:
                fields = item.fields
                user_story = UserStory(
                    id=item.id,
                    title=fields.get('System.Title', 'No Title'),
                    description=fields.get('System.Description', ''),
                    state=fields.get('System.State', 'Unknown'),
                    acceptance_criteria=fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', ''),
                    assigned_to=fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned')
                )
                user_stories.append(user_story)
                print(f"✅ Loaded user story: {user_story.title} (ID: {user_story.id})")

            return user_stories

        except Exception as e:
            print(f"❌ Error fetching user stories: {e}")
            raise

    def get_commits_for_user_story(self, user_story_id: int) -> List[Commit]:
        """Get commits associated with a user story using Azure DevOps SDK"""
        try:
            # Get work item with relations using SDK
            work_item = self.wit_client.get_work_item(
                id=user_story_id,
                expand='Relations',
                project=self.project
            )
            
            commits = []
            relations = work_item.relations or []

            print(f"📎 Found {len(relations)} relations for work item {user_story_id}")

            for relation in relations:
                rel_type = relation.rel
                rel_name = relation.attributes.get('name', '') if relation.attributes else ''
                
                print(f"  🔗 Processing relation: {rel_type} - {rel_name}")
                
                if (rel_type == 'ArtifactLink' and 
                    rel_name == 'Fixed in Commit'):
                    
                    commit_url = relation.url
                    print(f"  📌 Commit URL: {commit_url}")
                    
                    # Handle vstfs:// URL format
                    if commit_url.startswith('vstfs:///Git/Commit/'):
                        # Extract from vstfs URL format: vstfs:///Git/Commit/{projectId}%2F{repoId}%2F{commitId}
                        parts = commit_url.split('/')
                        if len(parts) >= 6:
                            # The commit part is the last segment
                            commit_part = parts[-1]
                            # Split by %2F to get project, repo, commit
                            commit_parts = commit_part.split('%2F')
                            if len(commit_parts) >= 3:
                                project_id = commit_parts[0]
                                repository_id = commit_parts[1]
                                commit_id = commit_parts[2]
                                
                                print(f"  🔍 Extracted: project={project_id}, repo={repository_id}, commit={commit_id}")
                                
                                try:
                                    # Use Git client to get commit details
                                    commit = self.git_client.get_commit(
                                        commit_id=commit_id,
                                        repository_id=repository_id,
                                        project=self.project
                                    )
                                    
                                    commits.append(Commit(
                                        commit_id=commit.commit_id,
                                        message=commit.comment or 'No message',
                                        author=commit.author.name if commit.author else 'Unknown',
                                        date=commit.author.date if commit.author else '',
                                        repository=repository_id
                                    ))
                                    print(f"  ✅ Found commit: {commit.commit_id[:8]} - {commit.comment[:50] if commit.comment else 'No message'}...")
                                    
                                except Exception as e:
                                    print(f"  ⚠️ Error fetching commit with Git client: {e}")

            print(f"✅ Found {len(commits)} commits for user story {user_story_id}")
            return commits

        except Exception as e:
            print(f"❌ Error fetching commits for user story {user_story_id}: {e}")
            return []
        
    def get_user_stories_with_commits(self, iteration_path: Optional[str] = None) -> List[UserStory]:
        """Get only user stories that have associated commits"""
        try:
            print("📋 Fetching user stories from Azure DevOps...")
            all_user_stories = self.get_user_stories(iteration_path)
            
            if not all_user_stories:
                return []
            
            user_stories_with_commits = []
            skipped_count = 0
            
            print(f"\n🔍 Checking commits for {len(all_user_stories)} user stories...")
            
            for user_story in all_user_stories:
                print(f"\n📖 Checking user story: {user_story.title} (ID: {user_story.id})")
                
                commits = self.get_commits_for_user_story(user_story.id)
                
                if commits:
                    user_stories_with_commits.append(user_story)
                    print(f"✅ INCLUDED - User story has {len(commits)} commits")
                else:
                    skipped_count += 1
                    print(f"❌ SKIPPED - No commits found for user story")
            
            print(f"\n🎯 Filtering results:")
            print(f"   ✅ User stories with commits: {len(user_stories_with_commits)}")
            print(f"   ❌ User stories without commits: {skipped_count}")
            print(f"   📊 Total processed: {len(all_user_stories)}")
            
            return user_stories_with_commits
            
        except Exception as e:
            print(f"❌ Error filtering user stories with commits: {e}")
            raise

    def get_changes_for_commit(self, repository_id: str, commit_id: str) -> List[Dict]:
        """Get file changes for a specific commit"""
        try:
            # Use Git client to get changes
            changes = self.git_client.get_changes(
                commit_id=commit_id,
                repository_id=repository_id,
                project=self.project
            )
            
            # Convert changes to dict format for compatibility
            changes_list = []
            for change in changes.changes:
                changes_list.append({
                    'item': {
                        'path': change.item.path,
                        'isFolder': change.item.git_object_type == 'tree'
                    },
                    'changeType': change.change_type
                })
            
            return changes_list

        except Exception as e:
            print(f"Error fetching changes for commit {commit_id}: {e}")
            return []

    def get_file_content(self, repository_id: str, commit_id: str, file_path: str) -> Optional[str]:
        """Get content of a specific file from a commit"""
        try:
            # Use Git client to get file content
            item = self.git_client.get_item(
                path=file_path,
                repository_id=repository_id,
                project=self.project,
                version=commit_id
            )
            
            if item.content:
                return item.content
            else:
                print(f"⚠️ No content found for {file_path}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error fetching file content for {file_path}: {e}")
            return None

    def get_code_files_for_commit(self, repository_id: str, commit_id: str) -> List[CodeFile]:
        """Get all code files with content for a commit"""
        try:
            changes = self.get_changes_for_commit(repository_id, commit_id)
            code_files = []
            
            for change in changes:
                item = change.get('item', {})
                file_path = item.get('path', '')
                change_type = change.get('changeType', '')
                
                # Skip deleted files and non-code files
                if (change_type == 'delete' or 
                    item.get('isFolder', False) or
                    not self._is_code_file(file_path)):
                    continue
                
                # Get file content
                content = self.get_file_content(repository_id, commit_id, file_path)
                if content:
                    file_name = os.path.basename(file_path)
                    language = self._detect_language(file_path)
                    
                    code_files.append(CodeFile(
                        file_path=file_path,
                        file_name=file_name,
                        content=content,
                        language=language,
                        commit_id=commit_id,
                        repository=repository_id
                    ))
                    print(f"  📄 Found code file: {file_path}")

            print(f"✅ Found {len(code_files)} code files in commit {commit_id[:8]}")
            return code_files

        except Exception as e:
            print(f"❌ Error getting code files for commit {commit_id}: {e}")
            return []
        
    def test_connection(self) -> bool:
        """Test Azure DevOps connection"""
        try:
            # Use Core client to test connection
            core_client = self.connection.clients.get_core_client()
            projects = core_client.get_projects()
            
            project_names = [p.name for p in projects]
            print(f"✅ Connected to Azure DevOps. Available projects: {project_names}")
            
            # Check if our project exists
            if self.project in project_names:
                print(f"✅ Project '{self.project}' found")
                return True
            else:
                print(f"❌ Project '{self.project}' not found. Available: {project_names}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False

    def get_all_code_files_for_user_story(self, user_story_id: int) -> List[CodeFile]:
        """Get all code files for a user story across all commits"""
        commits = self.get_commits_for_user_story(user_story_id)
        all_code_files = []
        
        print(f"🔍 Processing {len(commits)} commits for user story {user_story_id}")
        
        for commit in commits:
            code_files = self.get_code_files_for_commit(commit.repository, commit.commit_id)
            all_code_files.extend(code_files)
        
        # Remove duplicates by file path
        unique_files = {}
        for file in all_code_files:
            unique_files[file.file_path] = file
        
        result = list(unique_files.values())
        print(f"✅ Total unique code files for user story {user_story_id}: {len(result)}")
        return result

    def _is_code_file(self, file_path: str) -> bool:
        """Check if file is a code file based on extension"""
        code_extensions = {
            '.py', '.java', '.js', '.ts', '.cpp', '.c', '.h', '.hpp', 
            '.cs', '.go', '.rs', '.php', '.rb', '.swift', '.kt', '.scala',
            '.html', '.css', '.xml', '.json', '.yaml', '.yml', '.md',
            '.sql', '.sh', '.bat', '.ps1', '.config', '.txt'
        }
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in code_extensions

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.java': 'java',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cpp': 'cpp', '.c': 'c', '.h': 'c', '.hpp': 'cpp',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html', '.css': 'css',
            '.xml': 'xml', '.json': 'json',
            '.yaml': 'yaml', '.yml': 'yaml',
            '.md': 'markdown',
            '.sql': 'sql',
            '.sh': 'shell', '.bat': 'batch', '.ps1': 'powershell',
            '.config': 'config', '.txt': 'text'
        }
        file_ext = os.path.splitext(file_path)[1].lower()
        return language_map.get(file_ext, 'unknown')

    def prepare_requirements_from_story(self, user_story: UserStory) -> Dict:
        """Prepare requirements dictionary from user story"""
        acceptance_criteria = []
        if user_story.acceptance_criteria:
            # Simple text extraction from acceptance criteria
            lines = user_story.acceptance_criteria.replace('<p>', '\n').replace('</p>', '\n').split('\n')
            for line in lines:
                trimmed = line.strip()
                if trimmed and len(trimmed) > 5 and not trimmed.startswith('<'):
                    acceptance_criteria.append(trimmed)
        
        if not acceptance_criteria:
            acceptance_criteria = [f'Implement {user_story.title}']

        functional_requirements = [
            f"Implement {user_story.title}",
            "Follow coding standards and best practices",
            "Include proper error handling",
            "Add necessary logging and monitoring",
            "Ensure code is maintainable and testable"
        ]

        description_lower = (user_story.description or '').lower()
        title_lower = user_story.title.lower()
        
        if 'security' in description_lower or 'security' in title_lower:
            functional_requirements.append("Implement security best practices")
            functional_requirements.append("Perform security validation")

        return {
            'user_stories': [user_story.title],
            'acceptance_criteria': acceptance_criteria,
            'description': user_story.description or '',
            'functional_requirements': functional_requirements,
            'security_requirements': [
                "Input validation for all user inputs",
                "Secure authentication and authorization",
                "Proper error handling without information disclosure",
                "Secure data storage and transmission",
                "Protection against common vulnerabilities"
            ],
            'azure_story_id': user_story.id
        }