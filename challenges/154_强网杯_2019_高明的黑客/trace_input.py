#!/usr/bin/env python3
"""
追踪用户输入：找到 $var = $_GET['xxx']，然后追踪 $var 的使用
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    dangerous_funcs = ['system', 'eval', 'exec', 'passthru', 'shell_exec', 'assert']
    
    found = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # 找到所有 $var = $_GET['xxx'] ?? ' ';
        for i, line in enumerate(lines):
            match = re.search(r'\$([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\$_GET\[\'([^\']+)\'\]', line)
            if match:
                var_name = match.group(1)
                get_param = match.group(2)
                
                # 检查这个变量是否在后面被用于危险函数
                for j in range(i+1, len(lines)):
                    for func in dangerous_funcs:
                        # 检查 func($var)
                        pattern = rf'{func}\s*\(\s*\${var_name}\s*\)'
                        if re.search(pattern, lines[j]):
                            # 检查变量是否被重新赋值
                            overwritten = False
                            for k in range(i+1, j):
                                if re.search(rf'\${var_name}\s*=', lines[k]):
                                    overwritten = True
                                    break
                            
                            if not overwritten:
                                # 检查是否在假if条件中
                                in_false_if = False
                                for k in range(j-1, max(-1, j-5), -1):
                                    if_match = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'\s*\)", lines[k])
                                    if if_match:
                                        left, right = if_match.groups()
                                        if left != right:
                                            in_false_if = True
                                            break
                                
                                if not in_false_if:
                                    found.append((php_file, j+1, func, var_name, get_param))
                                    print(f"[+] FOUND: {php_file}:{j+1} - {func}(${var_name}) from $_GET['{get_param}']")
    
    print(f"\n[*] Found {len(found)} candidates")
    return found

if __name__ == "__main__":
    main()
