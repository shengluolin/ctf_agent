#!/usr/bin/env python3
import os
import re

def analyze_file(filepath):
    """分析 PHP 文件，找出没有被覆盖的 shell 参数"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    results = []
    lines = content.split('\n')
    
    # 找出所有被覆盖的 GET/POST 参数
    overwritten_get = set()
    overwritten_post = set()
    
    for line in lines:
        # 匹配 $_GET['xxx'] = 'yyy' 或 $_POST['xxx'] = 'yyy'
        get_overwrite = re.search(r"\$_GET\['(\w+)'\]\s*=\s*", line)
        post_overwrite = re.search(r"\$_POST\['(\w+)'\]\s*=\s*", line)
        
        if get_overwrite:
            overwritten_get.add(get_overwrite.group(1))
        if post_overwrite:
            overwritten_post.add(post_overwrite.group(1))
    
    # 找危险函数调用
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
            
            if is_fake:
                continue
            
            # 检查参数是否被覆盖
            if method == 'GET' and param in overwritten_get:
                continue
            if method == 'POST' and param in overwritten_post:
                continue
            
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
            shells = analyze_file(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个没有被覆盖的 shell 入口点\n")
    
    for s in all_shells[:100]:
        print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}'])")
    
    # 保存完整列表
    with open('no_overwrite_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")
    
    print(f"\n完整列表已保存到 no_overwrite_shells.txt")

if __name__ == '__main__':
    main()
