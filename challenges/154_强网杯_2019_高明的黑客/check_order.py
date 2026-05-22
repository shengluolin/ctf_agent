#!/usr/bin/env python3
"""
检查覆盖顺序：找到先使用后覆盖的情况
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
    ]
    
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
                    
                    # 检查是否在当前行之前被覆盖
                    overwrite_pattern = rf"\$_{method}\['{param}'\]\s*="
                    overwritten_before = False
                    for k in range(i):
                        if re.search(overwrite_pattern, lines[k]):
                            overwritten_before = True
                            break
                    
                    # 检查是否在当前行之后被覆盖
                    overwritten_after = False
                    for k in range(i+1, len(lines)):
                        if re.search(overwrite_pattern, lines[k]):
                            overwritten_after = True
                            break
                    
                    # 如果先使用后覆盖，这是正常的（可以执行）
                    if overwritten_after and not overwritten_before:
                        # 还需要检查if条件
                        for j in range(i-1, max(-1, i-5), -1):
                            prev_line = lines[j].strip()
                            if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", prev_line)
                            if if_match:
                                left, right = if_match.groups()
                                if left == right:
                                    print(f"[+] EXECUTABLE: {php_file}:{i+1}")
                                    print(f"    {func}({method}['{param}']) - used before overwrite")
                                    print(f"    IF: if('{left}' == '{right}') TRUE")
                                    break
                                else:
                                    # 假条件，不可执行
                                    break

if __name__ == "__main__":
    main()
