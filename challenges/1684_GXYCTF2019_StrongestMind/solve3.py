#!/usr/bin/env python3
import os
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)

import requests
import re
import time

url = "http://0168c74c-dba0-47e7-b3fe-ec2262a377a3.node5.buuoj.cn:81/index.php"
session = requests.Session()
session.trust_env = False

for i in range(1010):
    try:
        # 获取页面
        resp = session.get(url, timeout=10)
        content = resp.text
        
        # 检查是否有真正的flag格式 (flag{xxx})
        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
        if flag_match:
            print(f"\n[+] Found flag at iteration {i}!")
            print(f"[+] FLAG: {flag_match.group()}")
            with open('/tmp/flag.txt', 'w') as f:
                f.write(flag_match.group())
            break
        
        # 检查是否被限速
        if "429 Too Many Requests" in content:
            print(f"[!] Rate limited at iteration {i}, waiting 3 seconds...")
            time.sleep(3)
            continue
        
        # 提取计算表达式
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', content)
        if not match:
            print(f"[-] No expression found at iteration {i}")
            print(content[:500])
            break
        
        num1 = int(match.group(1))
        op = match.group(2)
        num2 = int(match.group(3))
        
        # 计算答案
        if op == '+':
            answer = num1 + num2
        elif op == '-':
            answer = num1 - num2
        elif op == '*':
            answer = num1 * num2
        elif op == '/':
            answer = num1 // num2
        
        # 提交答案
        data = {'answer': str(answer)}
        resp = session.post(url, data=data, timeout=10)
        
        if i % 100 == 0:
            print(f"[*] Progress: {i}/1000")
        
        # 添加延迟避免限速
        time.sleep(0.2)
        
    except Exception as e:
        print(f"[!] Error at iteration {i}: {e}")
        time.sleep(2)

print("\n[*] Done!")
