#!/usr/bin/env python3
import os
import re

def analyze_file(filepath):
    """分析 PHP 文件，找出 POST 参数的 shell"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 记录 POST 参数覆盖位置
    post_overwrites = {}
    
    for i, line in enumerate(lines):
        post_match = re.search(r"\$_POST\['(\w+)'\]\s*=\s*", line)
        if post_match:
            param = post_match.group(1)
            if param not in post_overwrites:
                post_overwrites[param] = []
            post_overwrites[param].append(i)
    
    # 找所有危险函数调用
    results = []
    
    patterns = [
        r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_POST\['(\w+)'\]",
        r"\('exec'\)\s*\(\s*\$_POST\['(\w+)'\]",
        r"\('system'\)\s*\(\s*\$_POST\['(\w+)'\]",
        r"\('shell_exec'\)\s*\(\s*\$_POST\['(\w+)'\]",
        r"preg_replace\s*\([^)]*\/e[^)]*,\s*\$_POST\['(\w+)'\]",
    ]
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[0] in ['eval', 'system', 'exec', 'shell_exec', 'passthru', 'assert']:
                    func, param = groups
                else:
                    func = 'exec'
                    param = groups[-1]
                
                # 检查是否在永远为假的条件中
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
                
                # 检查参数是否在调用之前被覆盖
                if param in post_overwrites:
                    for ow_line in post_overwrites[param]:
                        if ow_line < i:
                            break
                    else:
                        results.append({
                            'file': os.path.basename(filepath),
                            'line': i + 1,
                            'func': func,
                            'method': 'POST',
                            'param': param
                        })
                else:
                    results.append({
                        'file': os.path.basename(filepath),
                        'line': i + 1,
                        'func': func,
                        'method': 'POST',
                        'param': param
                    })
    
    return results

def main():
    src_dir = 'src'
    all_shells = []
    
    print("正在分析所有 PHP 文件的 POST 参数...")
    for filename in os.listdir(src_dir):
        if filename.endswith('.php'):
            filepath = os.path.join(src_dir, filename)
            shells = analyze_file(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个可能有效的 POST shell 入口点\n")
    
    for s in all_shells[:50]:
        print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}'])")
    
    with open('post_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")

if __name__ == '__main__':
    main()
