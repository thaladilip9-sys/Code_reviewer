# flawed_auth_system.py
import sqlite3
import hashlib
import json
import subprocess
import pickle
import os
import sys

# Global variables - hardcoded secrets
SECRET_KEY = "my_super_secret_key_12345"
ADMIN_PASSWORD = "admin123"
API_KEY = "sk_live_1234567890abcdef"

class UserManager:
    def __init__(self):
        self.conn = sqlite3.connect('users.db')
        self.create_table()
    
    def create_table(self):
        # SQL injection vulnerability - string formatting
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            is_admin INTEGER DEFAULT 0
        )
        """
        self.conn.execute(query)
        self.conn.commit()
    
    def register_user(self, username, password, email):
        # No input validation
        # Weak password hashing
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        # SQL injection vulnerability
        query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password_hash}', '{email}')"
        
        try:
            self.conn.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error: {e}")
            return False
    
    def login(self, username, password):
        # SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{hashlib.md5(password.encode()).hexdigest()}'"
        
        cursor = self.conn.execute(query)
        user = cursor.fetchone()
        
        if user:
            return user
        return None
    
    def get_user_by_id(self, user_id):
        # Another SQL injection
        query = f"SELECT * FROM users WHERE id = {user_id}"
        cursor = self.conn.execute(query)
        return cursor.fetchone()
    
    def delete_user(self, username):
        # Dangerous function with no authorization check
        query = f"DELETE FROM users WHERE username = '{username}'"
        self.conn.execute(query)
        self.conn.commit()

class ConfigManager:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        # Unsafe deserialization
        if os.path.exists('config.pickle'):
            with open('config.pickle', 'rb') as f:
                return pickle.load(f)
        return {}
    
    def save_config(self, config):
        # Unsafe serialization
        with open('config.pickle', 'wb') as f:
            pickle.dump(config, f)
    
    def execute_command(self, command):
        # Command injection vulnerability
        result = subprocess.check_output(command, shell=True)
        return result.decode()

class DataProcessor:
    def process_data(self, data):
        # No input validation
        # Using eval - huge security risk
        if isinstance(data, str):
            try:
                result = eval(data)
                return result
            except:
                return None
        return data
    
    def read_file(self, file_path):
        # Path traversal vulnerability
        with open(file_path, 'r') as f:
            return f.read()
    
    def write_file(self, file_path, content):
        # No path validation
        with open(file_path, 'w') as f:
            f.write(content)

def create_admin_user():
    # Hardcoded credentials
    manager = UserManager()
    password_hash = hashlib.md5(ADMIN_PASSWORD.encode()).hexdigest()
    query = f"INSERT OR REPLACE INTO users (username, password, email, is_admin) VALUES ('admin', '{password_hash}', 'admin@example.com', 1)"
    manager.conn.execute(query)
    manager.conn.commit()

def insecure_deserialization(data):
    # Critical security flaw - arbitrary code execution
    return pickle.loads(data)

def broken_auth_check(user_id, action):
    # Broken access control
    user_manager = UserManager()
    user = user_manager.get_user_by_id(user_id)
    
    if user:
        # No proper authorization check
        if action == "delete_user" and user[4] == 1:  # is_admin check
            return True
        return user[4] == 1  # Anyone who is admin can do anything
    return False

def weak_random():
    # Using weak random number generator
    import random
    return random.randint(1000, 9999)

def unsafe_logging(user_input):
    # Logging sensitive information
    print(f"User entered: {user_input}")
    # Logging passwords in plain text
    with open('app.log', 'a') as f:
        f.write(f"User action: {user_input}\n")

def mass_assignment_vulnerability(user_data):
    # Mass assignment vulnerability
    user_manager = UserManager()
    
    # No filtering of user-provided data
    username = user_data.get('username')
    password = user_data.get('password')
    email = user_data.get('email')
    is_admin = user_data.get('is_admin', 0)  # User can set themselves as admin!
    
    password_hash = hashlib.md5(password.encode()).hexdigest()
    query = f"INSERT INTO users (username, password, email, is_admin) VALUES ('{username}', '{password_hash}', '{email}', {is_admin})"
    
    user_manager.conn.execute(query)
    user_manager.conn.commit()

def xss_vulnerability(user_input):
    # XSS vulnerability - no output encoding
    response = f"""
    <html>
        <body>
            <h1>Welcome!</h1>
            <div>{user_input}</div>
        </body>
    </html>
    """
    return response

def insecure_direct_object_reference(user_id):
    # Insecure Direct Object Reference
    user_manager = UserManager()
    
    # No authorization check - users can access any user's data
    user = user_manager.get_user_by_id(user_id)
    return user

def code_injection():
    # Dynamic code execution
    code = input("Enter code to execute: ")
    exec(code)

def buffer_overflow_risk():
    # Potential buffer overflow (in Python context)
    large_string = "A" * 1000000
    # Processing without size checks
    processed = large_string.upper()
    return processed

def resource_exhaustion():
    # Resource exhaustion risk
    results = []
    for i in range(1000000):
        results.append("x" * 1000)
    return results

def improper_error_handling():
    # Revealing too much information in errors
    try:
        user_manager = UserManager()
        user = user_manager.get_user_by_id("invalid_id")
        return user
    except Exception as e:
        # Exposing stack trace and system information
        raise Exception(f"Database error: {str(e)}")

def security_misconfiguration():
    # Security misconfiguration
    import django
    # Debug mode enabled in production
    DEBUG = True
    
    # Exposing framework information
    print(f"Django version: {django.get_version()}")
    
    # Weak CORS settings
    CORS_ORIGIN_ALLOW_ALL = True

def using_deprecated_libraries():
    # Using deprecated/insecure libraries
    import md5  # Deprecated and insecure
    import sha  # Deprecated
    
    hash1 = md5.new("password".encode()).hexdigest()
    hash2 = sha.new("password".encode()).hexdigest()
    return hash1, hash2

def no_input_validation(data):
    # Complete lack of input validation
    return data.upper()

def hardcoded_cryptographic_key():
    # Hardcoded cryptographic key
    key = "this_is_a_secret_key_do_not_use_in_production"
    return key

def main():
    print("Flawed Authentication System")
    
    # Create admin user with hardcoded password
    create_admin_user()
    
    manager = UserManager()
    
    # Example usage with vulnerabilities
    user_input = input("Enter username: ")
    password = input("Enter password: ")
    
    # No rate limiting
    user = manager.login(user_input, password)
    
    if user:
        print("Login successful!")
        
        # Insecure direct object reference
        user_id = input("Enter user ID to view: ")
        user_data = insecure_direct_object_reference(user_id)
        print(f"User data: {user_data}")
        
        # Command injection example
        config_manager = ConfigManager()
        command = input("Enter command to execute: ")
        result = config_manager.execute_command(command)
        print(f"Command result: {result}")
        
    else:
        print("Login failed!")

if __name__ == "__main__":
    main()