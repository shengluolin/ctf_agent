#!/usr/bin/env python3
"""
找到真正可执行的webshell
条件：
1. 参数没有被覆盖
2. 没有被假条件包围（if('xxx' == 'yyy')）
"""
import os
import re

SRC_DIR = "src"

def is_real_shell(content, param, method, func):
    """
    检查是否是真正可执行的shell
    """
    lines = content.split('\n')
    
    # 找到危险函数调用的位置
    pattern = rf"{func}\s*\(\s*\$_{method}\['{param}'\]"
    
    for i, line in enumerate(lines):
        if re.search(pattern, line):
            # 检查是否在假条件中
            # 向上查找最近的if语句
            for j in range(i-1, max(-1, i-10), -1):
                prev_line = lines[j].strip()
                # 检查是否是 if('xxx' == 'yyy') 形式的假条件
                if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", prev_line)
                if if_match:
                    left, right = if_match.groups()
                    if left != right:
                        # 假条件，不可执行
                        return False
                    else:
                        # 真条件，可执行
                        break
                # 如果遇到非if的语句，说明不在条件中
                if prev_line and not prev_line.startswith('//') and not prev_line.startswith('/*') and '{' not in prev_line:
                    break
            
            # 检查参数是否被覆盖
            overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
            for k in range(i):
                if re.search(overwrite_pattern, lines[k]):
                    return False
            
            return True
    
    return False

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
        (r"passthru\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'passthru'),
        (r"passthru\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'passthru'),
    ]
    
    real_shells = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        for pattern, method, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                if is_real_shell(content, param, method, func):
                    real_shells.append((php_file, method, func, param))
                    print(f"[+] EXECUTABLE: {php_file} - {method} {func}({param})")
    
    print(f"\n[*] Found {len(real_shells)} executable shells")
    return real_shells

if __name__ == "__main__":
    shells = main()
    with open('executable_shells.txt', 'w') as f:
        for s in shells:
            f.write(f"{s[0]}:{s[1]}:{s[2]}:{s[3]}\n")
