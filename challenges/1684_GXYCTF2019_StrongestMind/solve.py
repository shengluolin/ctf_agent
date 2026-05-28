import requests
import re
import time

URL = "http://2a494b8a-533b-4bc9-a8d3-22994ad0712e.node5.buuoj.cn:81/index.php"
DELAY = 0.3

session = requests.Session()

# Get initial page to establish session
r = session.get(URL, timeout=10)
print(f"[*] Initial: {r.status_code}")

for i in range(1001):
    # Check if we got the flag (actual flag format, not just the word "flag")
    if 'flag{' in r.text:
        print(f"\n[SUCCESS] FLAG FOUND after round {i}!")
        # Extract flag
        flag_match = re.search(r'flag\{[^}]*\}', r.text)
        if flag_match:
            print(f"Flag: {flag_match.group(0)}")
        print(r.text)
        break

    # Parse math expression
    match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', r.text)
    if not match:
        print(f"\n[!] Round {i}: Could not parse expression")
        print(r.text[:500])
        break

    a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
    if op == '+':
        ans = a + b
    elif op == '-':
        ans = a - b
    elif op == '*':
        ans = a * b
    elif op == '/':
        ans = a // b
    else:
        print(f"\n[!] Unknown operator: {op}")
        break

    # Count display
    count_match = re.search(r'第 (\d+) 次成功啦', r.text)
    count = count_match.group(1) if count_match else '?'
    if i % 50 == 0:
        print(f"\r[*] Round {count}: {a} {op} {b} = {ans}", end="", flush=True)

    # Submit answer
    time.sleep(DELAY)
    r = session.post(URL, data={"answer": str(ans)}, timeout=10)

    if r.status_code != 200:
        print(f"\n[!] HTTP {r.status_code}")
        time.sleep(2)
        continue

print("\n[*] Done")
