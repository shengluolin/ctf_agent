#!/usr/bin/env python3
import requests
import re

url = "http://f12c0b09-f929-48ca-b216-fc61cafc19d3.node5.buuoj.cn:81/index.php"

session = requests.Session()

for i in range(1001):
    # Get the page
    resp = session.get(url)
    content = resp.text

    # Extract the math expression
    match = re.search(r'<br><br>([\d\s\+\-\*\/]+)<br><br>', content)
    if not match:
        print(f"[{i}] No expression found. Response: {content}")
        break

    expr = match.group(1).strip()
    # Calculate the result
    result = eval(expr)

    # Check current progress
    progress_match = re.search(r'第 (\d+) 次成功啦', content)
    if progress_match:
        progress = int(progress_match.group(1))
        print(f"[Round {i}] Progress: {progress}/1000 | {expr} = {result}")
    else:
        print(f"[Round {i}] {expr} = {result}")

    # Submit the answer
    resp = session.post(url, data={"answer": str(result)})
    content = resp.text

    # Check if we got the flag (look for flag pattern)
    flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
    if flag_match:
        print(f"\n[+] FLAG: {flag_match.group()}")
        break

print("Done!")
