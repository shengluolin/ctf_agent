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
session.trust_env = False  # 忽略系统代理

for i in range(1005):
    try:
        # 获取页面
        resp = session.get(url, timeout=10)
        content = resp.text
        
        # 检查是否有真正的flag格式
        flag_match = re.search(r'flag\{[^}]+\}', content, re.IGNORECASE)
        if flag_match:
            print(f"\n[+] Found flag at iteration {i}!")
            print(f"[+] FLAG: {flag_match.group()}")
            break
        
        # 检查当前进度
        progress_match = re.search(r'第 (\d+) 次成功', content)
        if progress_match:
            current_count = int(progress_match.group(1))
            if i % 50 == 0:
                print(f"[*] Server count: {current_count}, Local iteration: {i}")
        
        # 提取计算表达式
        match = re.search(r'(\d+)\s*([+\-*/])\s*(\d+)', content)
        if not match:
            print(f"[-] No expression found at iteration {i}")
            print(content)
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
        
        # 添加延迟避免限速
        time.sleep(0.15)
        
    except Exception as e:
        print(f"[!] Error at iteration {i}: {e}")
        time.sleep(2)

print("\n[*] Final response:")
try:
    final_resp = session.get(url, timeout=10)
    print(final_resp.text)
except Exception as e:
    print(f"Error: {e}")
