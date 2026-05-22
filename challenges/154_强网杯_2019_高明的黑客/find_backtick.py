#!/usr/bin/env python3
"""
找到没有被变量覆盖的反引号执行
"""
import os
import re

SRC_DIR = "src"

def main():
    php_files = [f for f in os.listdir(SRC_DIR) if f.endswith('.php')]
    
    # 匹配 echo `{$_GET['xxx']}`;
    pattern = r"echo\s*`\{\\\$_GET\['([^']+)'\]\}`"
    
    candidates = []
    
    for php_file in php_files:
        filepath = os.path.join(SRC_DIR, php_file)
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                param = match.group(1)
                # 检查是否被覆盖
                overwrite_pattern = rf"\$_GET\['{param}'\]\s*="
                overwritten = False
                for j in range(i):
                    if re.search(overwrite_pattern, lines[j]):
                        overwritten = True
                        break
                
                if not overwritten:
                    candidates.append((php_file, i+1, param))
                    print(f"[+] NO OVERWRITE: {php_file}:{i+1} - echo `{{$_GET['{param}']}}`")
    
    print(f"\n[*] Found {len(candidates)} candidates")
    return candidates

if __name__ == "__main__":
    main()
