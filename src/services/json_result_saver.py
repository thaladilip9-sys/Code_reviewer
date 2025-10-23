import os
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

class JSONResultSaver:
    """Save code review node results as a list of sessions in a single JSON file"""
    
    def __init__(self, output_base_dir: str = "code_review_reports"):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)
        self.sessions_file = os.path.join(output_base_dir, "sessions.json")
        self.current_session_data = {}  # Store current session data in memory
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def _load_sessions(self) -> List[Dict]:
        """Load existing sessions from file"""
        if os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_sessions(self, sessions: List[Dict]) -> None:
        """Save sessions to file"""
        with open(self.sessions_file, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, indent=2, ensure_ascii=False)
    
    def save_node_result(self, session_id: str, node_name: str, result_message: str) -> str:
        """
        Save the result message of a specific node with node name as key
        
        Args:
            session_id: Unique session identifier
            node_name: Name of the node (e.g., 'standards_check', 'requirement_validation')
            result_message: The result message from the node
            
        Returns:
            Path to the saved JSON file
        """
        # Initialize current session data if not exists
        if session_id not in self.current_session_data:
            self.current_session_data[session_id] = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Add node result to current session
        self.current_session_data[session_id][node_name] = result_message
        
        # Load existing sessions
        sessions = self._load_sessions()
        
        # Find existing session or create new one
        session_found = False
        for session in sessions:
            if session.get("session_id") == session_id:
                session[node_name] = result_message
                session_found = True
                break
        
        # If session not found, add new session
        if not session_found:
            new_session = {
                "session_id": session_id,
                "timestamp": self.current_session_data[session_id]["timestamp"]
            }
            new_session[node_name] = result_message
            sessions.append(new_session)
        
        # Save all sessions to file
        self._save_sessions(sessions)
        
        return self.sessions_file
    
    def get_session_results(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve all results for a specific session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary containing all session results
        """
        sessions = self._load_sessions()
        
        for session in sessions:
            if session.get("session_id") == session_id:
                return session
        
        return {"error": f"Session {session_id} not found"}
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Retrieve all sessions
        
        Returns:
            List of all sessions
        """
        return self._load_sessions()