#!/usr/bin/env python3
"""
找到真正可执行的shell：没有被覆盖且没有被假条件包围
"""
import os
import re

SRC_DIR = "src"

def check_if_before(lines, line_num):
    """检查前面的if条件"""
    for j in range(line_num-1, max(-1, line_num-10), -1):
        line = lines[j].strip()
        # if('xxx' == 'yyy')
        match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
        if match:
            left, right = match.groups()
            return left == right  # True表示条件为真
        # if('xxx' != 'yyy')
        match = re.search(r"if\s*\(\s*'([^']+)'\s*!=\s*'([^']+)'\s*\)", line)
        if match:
            left, right = match.groups()
            return left != right
        # 遇到非if语句就停止
        if line and not line.startswith('//') and not line.startswith('/*'):
            if 'if' not in line and '{' not in line and '}' not in line:
                return None  # 没有if条件
    return None

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'system'),
        (r"system\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'eval'),
        (r"eval\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'exec'),
        (r"exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'assert'),
        (r"assert\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'assert'),
    ]
    
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for pattern, func in patterns:
            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    param = match.group(1)
                    method = 'GET' if 'GET' in line else 'POST'
                    
                    # 检查是否被覆盖
                    overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
                    for k in range(i):
                        if re.search(overwrite_pattern, lines[k]):
                            break
                    else:
                        # 没有被覆盖，检查if条件
                        condition = check_if_before(lines, i)
                        if condition is True or condition is None:
                            found.append((php_file, i+1, method, func, param, condition))
                            if condition is True:
                                print(f"[+] TRUE IF: {php_file}:{i+1} - {method} {func}({param})")
                            else:
                                print(f"[+] NO IF: {php_file}:{i+1} - {method} {func}({param})")
    
    print(f"\n[*] Found {len(found)} potentially executable shells")
    return found

if __name__ == "__main__":
    found = main()
    # 保存结果
    with open('real_executable.txt', 'w') as f:
        for item in found:
            f.write(f"{item[0]}:{item[1]}:{item[2]}:{item[3]}:{item[4]}\n")
