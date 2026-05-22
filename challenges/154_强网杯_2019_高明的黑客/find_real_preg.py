#!/usr/bin/env python3
"""
找到真正可执行的preg_replace /e调用
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
                if re.search(overwrite_pattern, content[:content.find(line)]):
                    continue
                
                # 检查是否在假if条件中
                in_false_if = False
                for j in range(i-1, max(-1, i-5), -1):
                    prev_line = lines[j].strip()
                    if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", prev_line)
                    if if_match:
                        left, right = if_match.groups()
                        if left != right:
                            in_false_if = True
                            break
                
                if not in_false_if:
                    found.append((php_file, i+1, param))
                    print(f"[+] EXECUTABLE: {php_file}:{i+1} - preg_replace /e with $_GET['{param}']")
    
    print(f"\n[*] Found {len(found)} executable preg_replace calls")
    return found

if __name__ == "__main__":
    main()
