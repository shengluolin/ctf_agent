#!/usr/bin/env python3
import os
import re

def analyze_php_file(filepath):
    """分析 PHP 文件，找出真正可执行的 shell"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 危险函数及其参数提取
    patterns = [
        (r'eval\s*\(\s*\$_GET\[\'(\w+)\'\]', 'eval', 'GET'),
        (r'eval\s*\(\s*\$_POST\[\'(\w+)\'\]', 'eval', 'POST'),
        (r'system\s*\(\s*\$_GET\[\'(\w+)\'\]', 'system', 'GET'),
        (r'system\s*\(\s*\$_POST\[\'(\w+)\'\]', 'system', 'POST'),
        (r'exec\s*\(\s*\$_GET\[\'(\w+)\'\]', 'exec', 'GET'),
        (r'exec\s*\(\s*\$_POST\[\'(\w+)\'\]', 'exec', 'POST'),
        (r'shell_exec\s*\(\s*\$_GET\[\'(\w+)\'\]', 'shell_exec', 'GET'),
        (r'shell_exec\s*\(\s*\$_POST\[\'(\w+)\'\]', 'shell_exec', 'POST'),
        (r'passthru\s*\(\s*\$_GET\[\'(\w+)\'\]', 'passthru', 'GET'),
        (r'passthru\s*\(\s*\$_POST\[\'(\w+)\'\]', 'passthru', 'POST'),
        (r'assert\s*\(\s*\$_GET\[\'(\w+)\'\]', 'assert', 'GET'),
        (r'assert\s*\(\s*\$_POST\[\'(\w+)\'\]', 'assert', 'POST'),
    ]
    
    results = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        for pattern, func, method in patterns:
            match = re.search(pattern, line)
            if match:
                param = match.group(1)
                
                # 检查是否在永远为假的条件中
                # 向上查找最近的 if 语句
                is_fake = False
                for j in range(max(0, i-10), i):
                    prev_line = lines[j]
                    # 检查 if ('xxx' == 'yyy') 模式
                    if_match = re.search(r"if\s*\(\s*['\"](\w+)['\"]\s*==\s*['\"](\w+)['\"]\s*\)", prev_line)
                    if if_match:
                        left, right = if_match.groups()
                        if left != right:
                            is_fake = True
                            break
                    # 检查 if (function_exists(...))
                    if 'function_exists' in prev_line:
                        is_fake = True
                        break
                
                if not is_fake:
                    results.append({
                        'file': os.path.basename(filepath),
                        'line': i + 1,
                        'func': func,
                        'method': method,
                        'param': param,
                        'code': line.strip()
                    })
    
    return results

def main():
    src_dir = 'src'
    all_shells = []
    
    print("正在分析所有 PHP 文件...")
    for filename in os.listdir(src_dir):
        if filename.endswith('.php'):
            filepath = os.path.join(src_dir, filename)
            shells = analyze_php_file(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个可能有效的 shell 入口点\n")
    
    # 按文件分组
    file_shells = {}
    for s in all_shells:
        if s['file'] not in file_shells:
            file_shells[s['file']] = []
        file_shells[s['file']].append(s)
    
    # 输出前 100 个
    for i, s in enumerate(all_shells[:100]):
        print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}'])")
    
    # 保存完整列表
    with open('potential_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")
    
    print(f"\n完整列表已保存到 potential_shells.txt")

if __name__ == '__main__':
    main()
