"""Add hint directly to SQLite DB."""
import sqlite3
from datetime import datetime

hint_content = """KEY FACTS FOR THIS CHALLENGE:
1. PHP files are in src/ directory (3002 files, random names like A00UTldNShN.php)
2. Each file has many dangerous calls like: system($_GET['param'] ?? ' ')
3. Most are fake - inside false if conditions like if('abc'=='xyz') or params overwritten before use via $_GET['param']=' '
4. The CORRECT approach: dynamic testing with unique markers

WORKING PSEUDOCODE:
- For each .php file in src/:
  - Extract all $_GET params used in system()/passthru()/exec() calls
  - Regex: r"system\\(\\$_GET['\\\"]([^'\\\"]+)['\\\"]"
  - For each param: send GET request to BASE_URL+/src/+filename+?+param+=echo MARKER123
  - If MARKER123 appears in response: THAT IS THE REAL BACKDOOR
  - Then: send ?param=cat /flag to get the flag
- Use 3 threads with 0.3s delay between requests
- Test about 5000 unique system/passthru GET params - takes ~8 minutes

CRITICAL: URL must be BASE_URL + /src/ + filename (NOT BASE_URL + filename)
CRITICAL: The regex must match $_GET (with dollar sign and underscore), not generic variables
CRITICAL: The www.tar.gz is the download file, src/ is the extracted PHP files"""

conn = sqlite3.connect(r'E:\share\project\mypro\ctf-agent\data\dashboard.db')
conn.execute(
    "INSERT INTO hints (challenge_id, content, created_at) VALUES (?, ?, ?)",
    (154, hint_content, datetime.now().isoformat()),
)
conn.commit()

# Verify
rows = conn.execute(
    "SELECT id, challenge_id, substr(content, 1, 80) FROM hints WHERE challenge_id=154"
).fetchall()
for r in rows:
    print(f"  Hint #{r[0]}: [{r[1]}] {r[2]}...")
conn.close()
print("Done!")
