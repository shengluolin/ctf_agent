#!/usr/bin/env python3
"""
最终检查：找到所有危险函数调用，分析其是否可执行
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    # 所有危险函数模式
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'system'),
        (r"system\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'eval'),
        (r"eval\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'exec'),
        (r"exec\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'assert'),
        (r"assert\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'assert'),
        (r"passthru\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'passthru'),
        (r"passthru\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'passthru'),
        (r"shell_exec\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'shell_exec'),
        (r"shell_exec\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'shell_exec'),
        (r"\('exec'\)\s*\(\s*\$_POST\[\'([^\']+)\'\]\s*\?\?", 'POST', 'exec'),
        (r"\('system'\)\s*\(\s*\$_GET\[\'([^\']+)\'\]\s*\?\?", 'GET', 'system'),
        (r"echo\s*`\{\\\$_GET\[\'([^\']+)'\'\]\s*\?\?", 'GET', 'backtick'),
    ]
    
    all_calls = []
    
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
                    all_calls.append((php_file, i+1, method, func, param))
    
    print(f"[*] Total dangerous function calls: {len(all_calls)}")
    
    # 分析每个调用
    executable = []
    
    for php_file, line_num, method, func, param in all_calls:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        i = line_num - 1
        
        # 检查是否在注释中
        in_comment = False
        for j in range(i):
            if '/*' in lines[j]:
                in_comment = True
            if '*/' in lines[j]:
                in_comment = False
        if in_comment or lines[i].strip().startswith('//'):
            continue
        
        # 检查是否被覆盖
        overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
        for k in range(i):
            if re.search(overwrite_pattern, lines[k]):
                break
        else:
            # 没有被覆盖
            # 检查if条件
            for j in range(i-1, max(-1, i-5), -1):
                prev_line = lines[j].strip()
                if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", prev_line)
                if if_match:
                    left, right = if_match.groups()
                    if left == right:
                        # 条件为真！
                        executable.append((php_file, line_num, method, func, param))
                        print(f"[+] TRUE IF: {php_file}:{line_num} - {method} {func}({param})")
                        print(f"    if('{left}' == '{right}')")
                        break
                    else:
                        # 假条件
                        break
                elif prev_line and 'if' not in prev_line and '{' not in prev_line:
                    # 没有if条件，直接执行
                    executable.append((php_file, line_num, method, func, param))
                    print(f"[+] NO IF: {php_file}:{line_num} - {method} {func}({param})")
                    break
    
    print(f"\n[*] Executable calls: {len(executable)}")
    return executable

if __name__ == "__main__":
    main()
