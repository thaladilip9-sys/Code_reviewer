# bad_code_sample_v2.py
# Intentionally insecure & non-idiomatic Python for testing analyzers.

import os, sys, json, sqlite3, hashlib, subprocess

# Hardcoded credentials (Bandit will flag)
DB_PASSWORD = "P@ssw0rd123!"
API_KEY = "AKIAEXAMPLESECRETKEY"
SECRET_TOKEN = "s3cr3t-token-123"

# Global bad naming / shadowing builtins
X = 5
Y=10
list = [1,2,3]  # shadowing built-in

# Missing type hints and poor formatting
def add(a,b):
  return a +  b

# Function returning wrong type (MyPy will complain)
def greet(name: str) -> int:
    print("Hello " + name)
    return "Done"  # wrong return type

# Dangerous: shell command + no validation (Bandit)
def remove_all_logs():
    # no checks; dangerous hardcoded path and shell=True like behavior
    os.system("rm -rf /var/log")

# Dangerous use of subprocess with shell-like behavior (Bandit)
def run_user_command(cmd):
    # imagine cmd comes from user input — vulnerable to injection
    subprocess.Popen(cmd, shell=True)

# Insecure eval usage (Bandit)
def evaluate_user_expr(expr):
    # insecure: executing arbitrary expressions
    return eval(expr)

# Weak hashing (MD5) and use of secrets in code
def hash_password(pwd: str) -> str:
    # weak cryptography (md5) — Bandit will flag
    return hashlib.md5(pwd.encode()).hexdigest()

# SQL injection style string formatting + missing exception handling
def add_user_to_db(username, password):
    conn = sqlite3.connect("/tmp/users.db")
    cursor = conn.cursor()
    # BAD: direct string interpolation into SQL (SQLi)
    sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
    cursor.execute(sql)
    conn.commit()
    conn.close()

# File operation without exception handling (flat code)
def read_config():
    # no try/except — will crash if file missing or parse fails
    with open("/etc/myapp/config.json", "r") as f:
        cfg = json.load(f)
    return cfg

# Missing validation and no error handling for network-like operations
def send_token(token):
    # pretend to send token; no validation or safe storage
    print("Sending token:", token)
    # insecure: printing secret to logs

# Inconsistent indentation and mixed tabs/spaces
def weird_indent():
	if True:
	 print ("Tabs and spaces mixed")
	 print('This line uses tabs')

# Unused function and variables (style issues)
def UnusedFunction():
    pass

# Exposed secret in docstring / comments (some analyzers can flag)
"""
Doc: DB_PASSWORD = P@ssw0rd123!  # DO NOT COMMIT SECRETS
"""

if __name__=="__main__":
  # flat, no top-level exception handling: any error will crash the program
  greet("World")
  add(3 ,4)
  remove_all_logs()
  print("Hashed:", hash_password(DB_PASSWORD))
  run_user_command("ls -la /tmp")    # potentially unsafe
  print("Eval result:", evaluate_user_expr("2 + 3"))
  # Potential SQL injection demo
  add_user_to_db("alice", DB_PASSWORD)
  cfg = read_config()
  print(cfg.get("some_key"))
