#!/usr/bin/env python3
"""
找到关键参数：if条件中的字符串作为参数名
例如：if('abc' == 'def') system($_GET['abc'] ?? ' ');
这里'abc'出现在if条件和参数中
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 查找 if('xxx' == 'yyy') 形式
            if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
            if if_match:
                left, right = if_match.groups()
                
                # 检查下一行是否有危险函数使用这个参数
                if i+1 < len(lines):
                    next_line = lines[i+1]
                    # 检查是否使用了left或right作为参数
                    for param in [left, right]:
                        if re.search(rf"\$_GET\['{param}'\]", next_line) or \
                           re.search(rf"\$_POST\['{param}'\]", next_line):
                            # 找到了！
                            # 检查if条件是否为真
                            condition_true = (left == right)
                            if condition_true:
                                found.append((php_file, i+1, param, line.strip(), next_line.strip()))
                                print(f"[+] TRUE CONDITION: {php_file}:{i+1}")
                                print(f"    IF: {line.strip()}")
                                print(f"    EXEC: {next_line.strip()}")
    
    print(f"\n[*] Found {len(found)} shells with true conditions")
    return found

if __name__ == "__main__":
    main()
