#!/usr/bin/env python3
"""
找到if条件中的字符串与参数名匹配的情况
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 查找 if('xxx' == 'yyy')
            if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
            if if_match:
                left, right = if_match.groups()
                
                # 检查下一行是否有使用left或right作为参数的危险函数
                if i+1 < len(lines):
                    next_line = lines[i+1]
                    # 检查是否使用了left作为参数
                    if re.search(rf"\$_GET\['{left}'\]", next_line) or \
                       re.search(rf"\$_POST\['{left}'\]", next_line):
                        # 如果left == right，条件为真
                        if left == right:
                            print(f"[+] TRUE: {php_file}:{i+1}")
                            print(f"    if('{left}' == '{right}')")
                            print(f"    {next_line.strip()}")
                    # 检查是否使用了right作为参数
                    if re.search(rf"\$_GET\['{right}'\]", next_line) or \
                       re.search(rf"\$_POST\['{right}'\]", next_line):
                        if left == right:
                            print(f"[+] TRUE: {php_file}:{i+1}")
                            print(f"    if('{left}' == '{right}')")
                            print(f"    {next_line.strip()}")

if __name__ == "__main__":
    main()
