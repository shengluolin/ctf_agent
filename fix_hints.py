"""Fix hints with correct URL information."""
import sqlite3

hint = (
    "CRITICAL URL FIX: PHP files are served at the WEB ROOT, NOT in /src/ subdirectory!\n"
    "Correct: http://URL/A00UTldNShN.php?param=echo MARKER\n"
    "Wrong: http://URL/src/A00UTldNShN.php?param=echo MARKER (gives 404!)\n"
    "\n"
    "The src/ directory only exists inside www.tar.gz. On the live web server, "
    "PHP files are directly at the root path.\n"
    "\n"
    "Use: url = BASE_URL + '/' + filename + '?' + param + '=echo ' + marker\n"
    "\n"
    "Other key facts still apply:\n"
    "- 3002 PHP files with random names\n"
    "- Most dangerous calls are fake (false if conditions, param overwrites)\n"
    "- Dynamic marker testing is the correct approach\n"
    "- Use 3 threads, 0.3s delay\n"
    "- When found, use ?param=cat /flag to read the flag"
)

conn = sqlite3.connect(r'E:\share\project\mypro\ctf-agent\data\dashboard.db')
conn.execute('DELETE FROM hints WHERE challenge_id = 154')
conn.execute(
    'INSERT INTO hints (challenge_id, content, created_at) VALUES (?, ?, datetime("now"))',
    (154, hint),
)
conn.commit()

rows = conn.execute(
    'SELECT id, substr(content, 1, 100) FROM hints WHERE challenge_id = 154'
).fetchall()
for r in rows:
    print(f'Hint #{r[0]}: {r[1]}...')
conn.close()
print('Done - old hints cleared, new correct hint added')
