#!/usr/bin/env python3
"""
找到不在if条件中的危险函数调用
"""
import os
import re

SRC_DIR = "src"

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
    ]
    
    candidates = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for pattern, method, func in patterns:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    # 检查前面几行是否有if条件
                    has_if = False
                    for j in range(max(0, i-5), i+1):
                        if 'if(' in lines[j] or 'if (' in lines[j]:
                            has_if = True
                            break
                    
                    if not has_if:
                        # 检查参数是否被覆盖
                        param = re.search(r"\['([^\']+)\'\]", line)
                        if param:
                            param_name = param.group(1)
                            overwrite_pattern = rf"\$_{method}\['{param_name}'\]\s*="
                            overwritten = False
                            for k in range(i):
                                if re.search(overwrite_pattern, lines[k]):
                                    overwritten = True
                                    break
                            
                            if not overwritten:
                                candidates.append((php_file, i+1, method, func, param_name, line.strip()))
                                print(f"[+] NO IF: {php_file}:{i+1} - {method} {func}({param_name})")
                                print(f"    {line.strip()[:100]}")
    
    print(f"\n[*] Found {len(candidates)} candidates without if condition")
    return candidates

if __name__ == "__main__":
    candidates = main()
    with open('no_if_shells.txt', 'w') as f:
        for c in candidates:
            f.write(f"{c[0]}:{c[1]}:{c[2]}:{c[3]}:{c[4]}\n")
