#!/usr/bin/env python3
"""
找到没有被注释掉的可变函数调用
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    # 匹配 ('exec')($_POST['xxx'] ?? ' ');
    pattern = r"\('exec'\)\s*\(\s*\$_POST\['([^']+)'\]"
    
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        in_comment = False
        for i, line in enumerate(lines):
            if '/*' in line:
                in_comment = True
            if '*/' in line:
                in_comment = False
                continue
            
            if in_comment:
                continue
            
            match = re.search(pattern, line)
            if match:
                param = match.group(1)
                
                # 检查是否被覆盖
                overwrite_pattern = rf"\$_POST\['{param}'\]\s*="
                overwritten = False
                for k in range(i):
                    if re.search(overwrite_pattern, lines[k]):
                        overwritten = True
                        break
                
                if not overwritten:
                    # 检查if条件
                    for j in range(i-1, max(-1, i-5), -1):
                        prev_line = lines[j].strip()
                        if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", prev_line)
                        if if_match:
                            left, right = if_match.groups()
                            if left != right:
                                # 假条件
                                break
                            else:
                                # 真条件
                                found.append((php_file, i+1, param))
                                print(f"[+] TRUE IF: {php_file}:{i+1} - exec({param})")
                                break
                        elif prev_line and not prev_line.startswith('//') and 'if' not in prev_line:
                            # 没有if条件
                            found.append((php_file, i+1, param))
                            print(f"[+] NO IF: {php_file}:{i+1} - exec({param})")
                            break
    
    print(f"\n[*] Found {len(found)} candidates")
    return found

if __name__ == "__main__":
    main()
