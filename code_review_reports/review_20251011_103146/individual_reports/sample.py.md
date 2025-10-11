# Code Review: `sample.py`

**Language:** python

## 🔧 Ruff

```
E401 [*] Multiple imports on one line
 --> tmpqbz6rosm.py:4:1
  |
2 | # Intentionally insecure & non-idiomatic Python for testing analyzers.
3 |
4 | import os, sys, json, sqlite3, hashlib, subprocess
  | ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
5 |
6 | # Hardcoded credentials (Bandit will flag)
  |
help: Split imports

F401 [*] `sys` imported but unused
 --> tmpqbz6rosm.py:4:12
  |
2 | # Intentionally insecure & non-idiomatic Python for testing analyzers.
3 |
4 | import os, sys, json, sqlite3, hashlib, subprocess
  |            ^^^
5 |
6 | # Hardcoded credentials (Bandit will flag)
  |
help: Remove unused import: `sys`
```

## 🔧 Bandit

```
Run started:2025-10-11 05:01:46.129857

Test results:
>> Issue: [B404:blacklist] Consider possible security implications associated with the subprocess module.
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_imports.html#b404-import-subprocess
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:4:0
3	
4	import os, sys, json, sqlite3, hashlib, subprocess
5	

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 'P@ssw0rd123!'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:7:14
6	# Hardcoded credentials (Bandit will flag)
7	DB_PASSWORD = "P@ssw0rd123!"
8	API_KEY = "AKIAEXAMPLESECRETKEY"

--------------------------------------------------
>> Issue: [B105:hardcoded_password_string] Possible hardcoded password: 's3cr3t-token-123'
   Severity: Low   Confidence: Medium
   CWE: CWE-259 (https://cwe.mitre.org/data/definitions/259.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b105_hardcoded_password_string.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:9:15
8	API_KEY = "AKIAEXAMPLESECRETKEY"
9	SECRET_TOKEN = "s3cr3t-token-123"
10	

--------------------------------------------------
>> Issue: [B605:start_process_with_a_shell] Starting a process with a shell: Seems safe, but may be changed in the future, consider rewriting without shell
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b605_start_process_with_a_shell.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:28:4
27	    # no checks; dangerous hardcoded path and shell=True like behavior
28	    os.system("rm -rf /var/log")
29	

--------------------------------------------------
>> Issue: [B607:start_process_with_partial_path] Starting a process with a partial executable path
   Severity: Low   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b607_start_process_with_partial_path.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:28:4
27	    # no checks; dangerous hardcoded path and shell=True like behavior
28	    os.system("rm -rf /var/log")
29	

--------------------------------------------------
>> Issue: [B602:subprocess_popen_with_shell_equals_true] subprocess call with shell=True identified, security issue.
   Severity: High   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b602_subprocess_popen_with_shell_equals_true.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:33:4
32	    # imagine cmd comes from user input — vulnerable to injection
33	    subprocess.Popen(cmd, shell=True)
34	

--------------------------------------------------
>> Issue: [B307:blacklist] Use of possibly insecure function - consider using safer ast.literal_eval.
   Severity: Medium   Confidence: High
   CWE: CWE-78 (https://cwe.mitre.org/data/definitions/78.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/blacklists/blacklist_calls.html#b307-eval
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:38:11
37	    # insecure: executing arbitrary expressions
38	    return eval(expr)
39	

--------------------------------------------------
>> Issue: [B324:hashlib] Use of weak MD5 hash for security. Consider usedforsecurity=False
   Severity: High   Confidence: High
   CWE: CWE-327 (https://cwe.mitre.org/data/definitions/327.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b324_hashlib.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:43:11
42	    # weak cryptography (md5) — Bandit will flag
43	    return hashlib.md5(pwd.encode()).hexdigest()
44	

--------------------------------------------------
>> Issue: [B108:hardcoded_tmp_directory] Probable insecure usage of temp file/directory.
   Severity: Medium   Confidence: Medium
   CWE: CWE-377 (https://cwe.mitre.org/data/definitions/377.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b108_hardcoded_tmp_directory.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:47:27
46	def add_user_to_db(username, password):
47	    conn = sqlite3.connect("/tmp/users.db")
48	    cursor = conn.cursor()

--------------------------------------------------
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection vector through string-based query construction.
   Severity: Medium   Confidence: Low
   CWE: CWE-89 (https://cwe.mitre.org/data/definitions/89.html)
   More Info: https://bandit.readthedocs.io/en/1.8.6/plugins/b608_hardcoded_sql_expressions.html
   Location: C:\Users\thala\AppData\Local\Temp\tmpqbz6rosm.py:50:10
49	    # BAD: direct string interpolation into SQL (SQLi)
50	    sql = f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')"
51	    cursor.execute(sql)

--------------------------------------------------

Code scanned:
	Total lines of code: 52
	Total lines skipped (#nosec): 0
	Total potential issues skipped due to specifically being disabled (e.g., #nosec BXXX): 0

Run metrics:
	Total issues (by severity):
		Undefined: 0
		Low: 5
		Medium: 3
		High: 2
	Total issues (by confidence):
		Undefined: 0
		Low: 1
		Medium: 3
		High: 6
Files skipped (0):
```

## 🔧 MyPy

```
tmpqbz6rosm.py:23: error: Incompatible return value type (got "str", expected "int")  [return-value]
```

