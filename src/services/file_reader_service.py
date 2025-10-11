import os
import glob
from typing import List, Dict

class FileReader:
    """Read and process Python files from directory paths"""
    
    def __init__(self):
        self.supported_extensions = {'.py', '.java', '.js', '.ts', '.cpp', '.c', '.h', '.hpp'}
    
    def read_single_file(self, file_path: str) -> Dict:
        """Read a single file and return file info dictionary"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                code = file.read()
            
            file_name = os.path.basename(file_path)
            extension = os.path.splitext(file_path)[1].lower()
            
            return {
                "file_name": file_name,
                "file_path": file_path,
                "code": code,
                "extension": extension
            }
        except Exception as e:
            return {
                "file_name": os.path.basename(file_path),
                "file_path": file_path,
                "error": f"Failed to read file: {str(e)}"
            }
    
    def read_directory(self, directory_path: str, recursive: bool = True) -> List[Dict]:
        """Read all supported files from a directory"""
        files_info = []
        
        if not os.path.exists(directory_path):
            return [{"error": f"Directory does not exist: {directory_path}"}]
        
        pattern = "**/*" if recursive else "*"
        
        for ext in self.supported_extensions:
            search_pattern = os.path.join(directory_path, pattern + ext)
            for file_path in glob.glob(search_pattern, recursive=recursive):
                if os.path.isfile(file_path):
                    file_info = self.read_single_file(file_path)
                    files_info.append(file_info)
        
        return files_info
    
    def read_files_from_paths(self, paths: List[str]) -> List[Dict]:
        """Read files from multiple paths (files or directories)"""
        all_files = []
        
        for path in paths:
            if os.path.isfile(path):
                # Single file
                file_info = self.read_single_file(path)
                all_files.append(file_info)
            elif os.path.isdir(path):
                # Directory
                directory_files = self.read_directory(path)
                all_files.extend(directory_files)
            else:
                all_files.append({
                    "file_name": os.path.basename(path),
                    "file_path": path,
                    "error": "Path does not exist or is not a file/directory"
                })
        
        return all_files