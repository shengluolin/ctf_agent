#!/usr/bin/env python3
"""
综合检查：找出所有危险函数调用，分析其是否可执行
"""
import os
import re

SRC_DIR = "src"

def is_in_comment(lines, line_num):
    """检查是否在注释块中"""
    in_comment = False
    for i in range(line_num):
        if '/*' in lines[i]:
            in_comment = True
        if '*/' in lines[i]:
            in_comment = False
    return in_comment or lines[line_num].strip().startswith('//')

def is_after_false_if(lines, line_num):
    """检查是否在假if条件后"""
    for j in range(line_num-1, max(-1, line_num-10), -1):
        line = lines[j].strip()
        if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", line)
        if if_match:
            left, right = if_match.groups()
            return left != right  # True表示假条件
        # 遇到非if语句就停止
        if line and 'if' not in line and '{' not in line and '}' not in line and not line.startswith('//'):
            return False
    return False

def is_param_overwritten(lines, line_num, param, method):
    """检查参数是否被覆盖"""
    pattern = rf"\$_{method}\['{param}'\]\s*="
    for i in range(line_num):
        if re.search(pattern, lines[i]):
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
        (r"shell_exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'shell_exec'),
        (r"shell_exec\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'shell_exec'),
        (r"\('exec'\)\s*\(\s*\$_POST\[\'([^\']+)\'\]", 'POST', 'exec'),
        (r"\('system'\)\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'GET', 'system'),
        (r"echo\s*`\{\\\$_GET\['([^']+)'\]\}`", 'GET', 'backtick'),
    ]
    
    executable = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for pattern, method, func in patterns:
            for i, line in enumerate(lines):
                match = re.search(pattern, line)
                if match:
                    param = match.group(1)
                    
                    # 检查各种保护机制
                    in_comment = is_in_comment(lines, i)
                    after_false_if = is_after_false_if(lines, i)
                    param_overwritten = is_param_overwritten(lines, i, param, method)
                    
                    if not in_comment and not after_false_if and not param_overwritten:
                        executable.append((php_file, i+1, method, func, param, line.strip()))
                        print(f"[+] EXECUTABLE: {php_file}:{i+1} - {method} {func}({param})")
                        print(f"    Line: {line.strip()[:80]}")
    
    print(f"\n[*] Found {len(executable)} executable shells")
    return executable

if __name__ == "__main__":
    found = main()
    if found:
        with open('final_executable.txt', 'w') as f:
            for item in found:
                f.write(f"{item[0]}:{item[1]}:{item[2]}:{item[3]}:{item[4]}\n")
