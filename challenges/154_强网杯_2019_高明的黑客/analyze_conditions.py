#!/usr/bin/env python3
"""
分析危险函数调用的执行条件
"""
import os
import re

SRC_DIR = "src"

def analyze_if_condition(line):
    """分析if条件是否为真"""
    # if('xxx' == 'yyy') 形式
    match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
    if match:
        left, right = match.groups()
        return left == right
    
    # if('xxx' != 'yyy') 形式
    match = re.search(r"if\s*\(\s*'([^']+)'\s*!=\s*'([^']+)'\s*\)", line)
    if match:
        left, right = match.groups()
        return left != right
    
    return None  # 无法确定

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'system'),
        (r"system\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'eval'),
        (r"eval\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'exec'),
        (r"exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'assert'),
        (r"assert\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'assert'),
    ]
    
    executable = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for pattern, method, func in patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    param = re.search(r"\['([^\']+)\'\]", line).group(1)
                    
                    # 检查参数是否被覆盖
                    overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
                    overwritten = False
                    for k in range(i):
                        if re.search(overwrite_pattern, lines[k]):
                            overwritten = True
                            break
                    
                    if overwritten:
                        continue
                    
                    # 检查if条件
                    # 向上查找最近的if语句
                    condition_result = None
                    for j in range(i-1, max(-1, i-10), -1):
                        prev_line = lines[j].strip()
                        if prev_line.startswith('if'):
                            condition_result = analyze_if_condition(prev_line)
                            break
                    
                    if condition_result is True:
                        executable.append((php_file, i+1, method, func, param))
                        print(f"[+] EXECUTABLE: {php_file}:{i+1} - {method} {func}({param})")
                    elif condition_result is None:
                        # 没有if条件，可能是可执行的
                        executable.append((php_file, i+1, method, func, param))
                        print(f"[+] NO CONDITION: {php_file}:{i+1} - {method} {func}({param})")
    
    print(f"\n[*] Found {len(executable)} potentially executable shells")
    return executable

if __name__ == "__main__":
    main()
