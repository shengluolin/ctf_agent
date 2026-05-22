#!/usr/bin/env python3
"""
找到真正可执行的webshell - 检查参数是否被覆盖
"""
import os
import re

SRC_DIR = "src"

def check_param_overwrite(content, param, method='GET'):
    """
    检查参数是否在危险函数调用之前被覆盖
    返回: True表示没有被覆盖（可执行），False表示被覆盖
    """
    # 找到危险函数调用的行号
    pattern = rf"(system|eval|exec|passthru|shell_exec|assert)\s*\(\s*\$_{method}\['{param}'\]"
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        return False
    
    lines = content.split('\n')
    
    for match in matches:
        # 找到调用所在的行号
        call_pos = match.start()
        call_line = content[:call_pos].count('\n')
        
        # 检查在调用之前是否有参数覆盖
        # $_GET['xxx'] = '...' 或 $_POST['xxx'] = '...'
        overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
        
        for i, line in enumerate(lines[:call_line]):
            if re.search(overwrite_pattern, line):
                # 找到覆盖，这个shell不可执行
                return False
    
    return True

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    # 危险函数模式
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
        (r"shell_exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'shell_exec'),
        (r"shell_exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'shell_exec'),
    ]
    
    real_shells = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        for pattern, method, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                if check_param_overwrite(content, param, method):
                    real_shells.append((php_file, method, func, param))
                    print(f"[+] REAL: {php_file} - {method} {func}({param})")
    
    print(f"\n[*] Found {len(real_shells)} real shells")
    return real_shells

if __name__ == "__main__":
    shells = main()
    # 保存结果
    with open('real_shells_no_overwrite.txt', 'w') as f:
        for s in shells:
            f.write(f"{s[0]}:{s[1]}:{s[2]}:{s[3]}\n")
