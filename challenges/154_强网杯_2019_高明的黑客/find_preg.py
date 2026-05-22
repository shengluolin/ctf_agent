#!/usr/bin/env python3
"""
找到没有被覆盖的preg_replace /e调用
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    pattern = r"@preg_replace\s*\(\s*\"/[^\"]+/e\"\s*,\s*\$_GET\['([^']+)'\]"
    
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                param = match.group(1)
                
                # 检查是否被覆盖
                overwrite_pattern = rf"\$_GET\['{param}'\]\s*="
                if not re.search(overwrite_pattern, content[:content.find(line)]):
                    found.append((php_file, i+1, param))
                    print(f"[+] NO OVERWRITE: {php_file}:{i+1} - preg_replace /e with $_GET['{param}']")
    
    print(f"\n[*] Found {len(found)} candidates")
    return found

if __name__ == "__main__":
    main()
