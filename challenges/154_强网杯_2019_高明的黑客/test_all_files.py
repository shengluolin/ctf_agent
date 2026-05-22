#!/usr/bin/env python3
"""
测试所有PHP文件，寻找异常响应
"""
import os
import requests
import time

BASE_URL = "http://01de7a39-b84f-4e29-afb6-cc13ed331efc.node5.buuoj.cn:81"
SRC_DIR = "src"
DELAY = 0.05

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    session = requests.Session()
    
    for i, php_file in enumerate(php_files):
        url = f"{BASE_URL}/{php_file}"
        
        try:
            # 测试GET请求
            r = session.get(url, timeout=3)
            
            if r.status_code != 200:
                print(f"[{r.status_code}] {php_file}")
            elif 'error' in r.text.lower() or 'warning' in r.text.lower():
                # 检查是否有错误信息
                if 'Fatal error' in r.text:
                    print(f"[FATAL] {php_file}")
            
            if i % 500 == 0:
                print(f"[*] Tested {i}/{len(php_files)} files...", flush=True)
            
            time.sleep(DELAY)
            
        except Exception as e:
            pass
    
    print(f"\n[*] Done")

if __name__ == "__main__":
    main()
