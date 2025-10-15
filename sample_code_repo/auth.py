# src/auth.py
import os
import json
import sqlite3
from typing import Dict, Any
import hashlib
import base64

# Global variables - bad practice
DATABASE_PATH = "/tmp/users.db"
SECRET_KEY = "hardcoded_secret_key_12345"  # Hardcoded secret
ADMIN_PASSWORD = "admin123"  # Hardcoded password

class UserManager:
    def __init__(self):
        self.conn = None
        self.setup_database()
    
    def setup_database(self):
        """Setup database with SQL injection vulnerability"""
        self.conn = sqlite3.connect(DATABASE_PATH)
        cursor = self.conn.cursor()
        
        # No error handling
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT
            )
        ''')
        
        # Insert admin user with weak password
        cursor.execute(f"INSERT OR IGNORE INTO users (username, password, email) VALUES ('admin', '{ADMIN_PASSWORD}', 'admin@example.com')")
        self.conn.commit()
    
    def register_user(self, username: str, password: str, email: str) -> bool:
        """Register user with multiple security issues"""
        
        # No input validation
        if not username or not password:
            return False
        
        # Weak password check
        if len(password) < 4:  # Too short
            return False
        
        # SQL injection vulnerability
        cursor = self.conn.cursor()
        query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
        
        try:
            cursor.execute(query)
            self.conn.commit()
            return True
        except:
            return False
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login with security vulnerabilities"""
        
        # SQL injection
        cursor = self.conn.cursor()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            # Create JWT token without proper signing
            token_data = {
                "user_id": user[0],
                "username": user[1],
                "is_admin": user[1] == "admin"
            }
            
            # Weak token generation
            token = base64.b64encode(json.dumps(token_data).encode()).decode()
            return {"success": True, "token": token, "user": user[1]}
        
        return {"success": False, "error": "Invalid credentials"}
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data with IDOR vulnerability"""
        cursor = self.conn.cursor()
        
        # Insecure direct object reference
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor.execute(query)
        user = cursor.fetchone()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[3],
                "password": user[2]  # Exposing password!
            }
        return {}

def weak_hash_password(password: str) -> str:
    """Weak password hashing using MD5"""
    return hashlib.md5(password.encode()).hexdigest()

def validate_email(email: str) -> bool:
    """Poor email validation"""
    return "@" in email  # Very basic validation

def process_user_input(user_input: str) -> str:
    """No input sanitization"""
    # Potential XSS and injection issues
    return user_input.upper()

def unsafe_deserialize(data: str) -> Dict:
    """Unsafe deserialization"""
    return eval(data)  # Dangerous!

def divide_numbers(a: int, b: int) -> float:
    """No error handling for division by zero"""
    return a / b

def read_config_file(file_path: str) -> Dict:
    """Unsafe file reading"""
    with open(file_path, 'r') as f:  # No path validation
        return json.load(f)

def write_log(message: str):
    """Poor logging with potential log injection"""
    log_entry = f"LOG: {message}\n"
    with open("/tmp/app.log", "a") as f:
        f.write(log_entry)  # No sanitization

# Unused imports and variables
unused_variable = "This is never used"
another_unused = 42

# Poor function organization
def helper1():
    pass

def helper2():
    pass

def main_function():
    """Main function with multiple issues"""
    manager = UserManager()
    
    # Hardcoded credentials in code
    test_user = "test"
    test_pass = "test123"
    
    # Register user
    success = manager.register_user(test_user, test_pass, "test@example.com")
    print(f"Registration: {success}")
    
    # Login
    result = manager.login(test_user, test_pass)
    print(f"Login: {result}")
    
    # Get user data (IDOR vulnerability)
    user_data = manager.get_user_data(1)
    print(f"User data: {user_data}")
    
    # Demonstrate other vulnerabilities
    try:
        # Division by zero
        result = divide_numbers(10, 0)
    except Exception as e:
        print(f"Division error: {e}")
    
    # Weak hashing
    weak_hash = weak_hash_password("password123")
    print(f"Weak hash: {weak_hash}")
    
    # Unsafe deserialization
    malicious_data = "__import__('os').system('rm -rf /')"
    # unsafe_deserialize(malicious_data)  # Commented out for safety

if __name__ == "__main__":
    main_function()