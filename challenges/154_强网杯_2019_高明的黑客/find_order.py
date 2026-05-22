#!/usr/bin/env python3
"""
找到参数使用顺序：先使用后覆盖的情况
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    patterns = [
        (r"system\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'system'),
        (r"eval\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'eval'),
        (r"exec\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'exec'),
        (r"assert\s*\(\s*\$_GET\[\'([^\']+)\'\]", 'assert'),
        (r"echo\s*`\{\\\$_GET\['([^']+)'\]\}`", 'backtick'),
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
                    
                    # 检查是否在当前行之后被覆盖
                    overwrite_pattern = rf"\$_GET\['{param}'\]\s*="
                    for j in range(i+1, len(lines)):
                        if re.search(overwrite_pattern, lines[j]):
                            # 在使用之后被覆盖，这是正常的
                            break
                    else:
                        # 检查是否在使用之前被覆盖
                        for k in range(i):
                            if re.search(overwrite_pattern, lines[k]):
                                # 在使用之前被覆盖，不可执行
                                break
                        else:
                            # 没有被覆盖
                            found.append((php_file, i+1, func, param))
                            print(f"[+] NO OVERWRITE: {php_file}:{i+1} - {func}({param})")
    
    print(f"\n[*] Found {len(found)} candidates")
    return found

if __name__ == "__main__":
    main()
