"""Update hint for challenge 154 with comprehensive instructions."""
import sqlite3

hint = """CRITICAL INSTRUCTIONS - READ CAREFULLY:

1. URL FORMAT: PHP files are served at WEB ROOT, NOT in /src/!
   Correct: http://URL/filename.php?param=echo MARKER123
   Wrong: http://URL/src/filename.php (gives 404!)
   The src/ dir only exists inside www.tar.gz.

2. START YOUR SCRIPT WITH:
   import sys; sys.stdout.reconfigure(line_buffering=True)
   Or run with: python -u your_script.py
   This ensures output is NOT buffered.

3. STRATEGY - Dynamic marker testing:
   - Extract all $_GET params from system/passthru/exec calls
   - Regex pattern: system followed by dollar sign _GET with param name
   - For each: GET http://URL/filename.php?param=echo MARKER_file_param
   - If MARKER appears in response: THAT IS THE REAL BACKDOOR
   - Use 3 threads, 0.3s delay, print progress every 50 tests
   - When found: GET http://URL/filename.php?param=cat /flag

4. KEY FACTS:
   - 3002 PHP files, most dangerous calls are fake (false conditions, param overwrites)
   - You must TEST DYNAMICALLY - static analysis cannot distinguish real from fake
   - Estimated ~5000 params to test, takes ~8 min with 3 threads"""

conn = sqlite3.connect(r'E:\share\project\mypro\ctf-agent\data\dashboard.db')
conn.execute('DELETE FROM stdout_log WHERE challenge_id=154')
conn.execute('DELETE FROM hints WHERE challenge_id=154')
conn.execute(
    'INSERT INTO hints (challenge_id, content, created_at) VALUES (?, ?, datetime("now"))',
    (154, hint),
)
conn.commit()

r = conn.execute('SELECT id, used_in_attempt, length(content) FROM hints WHERE challenge_id=154').fetchall()
print('Hint updated:', r)
conn.close()
print('Done')
