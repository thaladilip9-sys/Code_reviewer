# src/utils.py
import pickle
import subprocess
import sys
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config = {}
    
    def load_config(self, config_path: str):
        """Unsafe pickle loading"""
        with open(config_path, 'rb') as f:
            self.config = pickle.load(f)  # Dangerous!
    
    def execute_command(self, command: str):
        """Command injection vulnerability"""
        # No input validation
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def read_arbitrary_file(self, file_path: str) -> str:
        """Path traversal vulnerability"""
        base_dir = Path("/app/data")
        target_file = base_dir / file_path  # No path sanitization
        
        with open(target_file, 'r') as f:
            return f.read()
    
    def unsafe_eval(self, expression: str):
        """Unsafe eval usage"""
        return eval(expression)

def create_user_object(data: dict):
    """Class with too many responsibilities"""
    class User:
        def __init__(self, data):
            self.data = data
            self.db_connection = None
            self.cache = {}
            self.logger = None
        
        def validate(self):
            # Too many validations in one method
            if 'email' in self.data:
                if '@' not in self.data['email']:
                    return False
            if 'password' in self.data:
                if len(self.data['password']) < 3:
                    return False
            if 'username' in self.data:
                if len(self.data['username']) < 2:
                    return False
            return True
        
        def save_to_db(self):
            # Mixing concerns
            pass
        
        def send_email(self):
            # Should not be here
            pass
        
        def generate_report(self):
            # Too many responsibilities
            pass
    
    return User(data)

# Global state manipulation
global_state = {}

def update_global_state(key: str, value: any):
    """Function with side effects"""
    global_state[key] = value
    # Also modifies external state
    with open("/tmp/state.json", "w") as f:
        import json
        json.dump(global_state, f)

# Poor exception handling
def risky_operation():
    try:
        # Too broad exception handling
        result = 10 / 0
    except:
        pass  # Silent failure

# Inconsistent naming
def GetData():
    return {"data": "value"}

def process_data():
    return GetData()

def CalculateTotal():
    return 100

# Dead code
def unused_function():
    return "This is never called"

def another_unused():
    print("Also never used")

# Long function with multiple responsibilities
def process_user_request(request_data: dict) -> dict:
    """Function doing too many things"""
    # Validation
    if 'user_id' not in request_data:
        return {"error": "Missing user_id"}
    
    # Database operation
    import sqlite3
    conn = sqlite3.connect("/tmp/app.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {request_data['user_id']}")
    user = cursor.fetchone()
    
    # Business logic
    if user:
        if user[3] == 'premium':  # Magic number
            discount = 0.1
        else:
            discount = 0.0
        
        # Calculation
        total = 100 * (1 - discount)
        
        # Formatting
        response = {
            "user": user[1],
            "total": total,
            "discount": discount
        }
        
        # Logging
        print(f"Processed request for user {user[1]}")
        
        return response
    
    return {"error": "User not found"}

if __name__ == "__main__":
    manager = ConfigManager()
    manager.execute_command("ls -la")  # Safe example, but pattern is dangerous