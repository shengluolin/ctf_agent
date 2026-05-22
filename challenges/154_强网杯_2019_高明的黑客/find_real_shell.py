#!/usr/bin/env python3
import os
import re

def analyze_file(filepath):
    """分析 PHP 文件，找出调用时还没被覆盖的 shell 参数"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    results = []
    lines = content.split('\n')
    
    # 找出所有危险函数调用及其行号
    dangerous_calls = []
    for i, line in enumerate(lines):
        match = re.search(r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST)\['(\w+)'\]", line)
        if match:
            func = match.group(1)
            method = match.group(2)
            param = match.group(3)
            
            # 检查是否在注释中
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue
            
            # 检查是否在 if 条件中（条件永远为假）
            is_fake = False
            for j in range(max(0, i-5), i):
                prev_line = lines[j]
                if_match = re.search(r"if\s*\(\s*['\"](\w+)['\"]\s*==\s*['\"](\w+)['\"]\s*\)", prev_line)
                if if_match:
                    left, right = if_match.groups()
                    if left != right:
                        is_fake = True
                        break
            
            if not is_fake:
                dangerous_calls.append({
                    'line': i,
                    'func': func,
                    'method': method,
                    'param': param
                })
    
    # 检查每个调用，看参数是否在调用之前被覆盖
    for call in dangerous_calls:
        call_line = call['line']
        param = call['param']
        method = call['method']
        
        # 检查在调用之前是否有覆盖
        is_overwritten_before = False
        for i in range(call_line):
            line = lines[i]
            pattern = rf"\$_{method}\['{param}'\]\s*=\s*"
            if re.search(pattern, line):
                is_overwritten_before = True
                break
        
        if not is_overwritten_before:
            results.append({
                'file': os.path.basename(filepath),
                'line': call_line + 1,
                'func': call['func'],
                'method': method,
                'param': param
            })
    
    return results

def main():
    src_dir = 'src'
    all_shells = []
    
    print("正在分析所有 PHP 文件...")
    for filename in os.listdir(src_dir):
        if filename.endswith('.php'):
            filepath = os.path.join(src_dir, filename)
            shells = analyze_file(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个有效的 shell 入口点\n")
    
    for s in all_shells[:50]:
        print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}'])")
    
    # 保存完整列表
    with open('valid_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")
    
    print(f"\n完整列表已保存到 valid_shells.txt")

if __name__ == '__main__':
    main()
