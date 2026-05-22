#!/usr/bin/env python3
"""
[BSidesCF 2020]Hurdles 解题脚本
题目需要通过一系列HTTP请求"跨栏"才能获取flag
"""

import requests
import hashlib

# 题目URL (需要替换为实际URL)
url = "http://example.com/hurdles/!"

# 1. 密码: open sesame 的 MD5 十六进制表示
password = hashlib.md5(b"open sesame").hexdigest()
print(f"[+] Password (MD5 of 'open sesame'): {password}")

# 2. 构造查询参数
# - get=flag: 获取flag
# - &=&=&=%00\n: 特殊参数名和值
params = {
    "get": "flag",
    "&=&=&": "%00\n"
}

# 3. 构造HTTP头
headers = {
    # User-Agent: 1337浏览器，版本号>9000
    "User-Agent": "1337 Browser v.9999",

    # X-Forwarded-For: 客户端IP为13.37.13.37，通过127.0.0.1代理
    "X-Forwarded-For": "13.37.13.37, 127.0.0.1",

    # Cookie: Fortune=6265 (RFC 6265 - HTTP State Management Mechanism)
    "Cookie": "Fortune=6265",

    # Accept: 只接受纯文本
    "Accept": "text/plain",

    # Accept-Language: 俄语
    "Accept-Language": "ru",

    # Origin: CORS来源
    "Origin": "https://ctf.bsidessf.net",

    # Referer: 来源页面
    "Referer": "https://ctf.bsidessf.net/challenges"
}

# 4. 发送PUT请求，带Basic认证
r = requests.put(url, params=params, auth=("player", password), headers=headers)

print(f"[+] Status: {r.status_code}")
print(f"[+] Body: {r.text}")

# 5. 从响应头获取flag
if "X-Ctf-Flag" in r.headers:
    print(f"[+] FLAG: {r.headers['X-Ctf-Flag']}")
