#!/usr/bin/env python3
import os
import re

def analyze_file_detailed(filepath):
    """详细分析 PHP 文件"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 记录每个参数的覆盖位置
    get_overwrites = {}  # param -> [line_numbers]
    post_overwrites = {}
    
    for i, line in enumerate(lines):
        get_match = re.search(r"\$_GET\['(\w+)'\]\s*=\s*", line)
        post_match = re.search(r"\$_POST\['(\w+)'\]\s*=\s*", line)
        
        if get_match:
            param = get_match.group(1)
            if param not in get_overwrites:
                get_overwrites[param] = []
            get_overwrites[param].append(i)
        
        if post_match:
            param = post_match.group(1)
            if param not in post_overwrites:
                post_overwrites[param] = []
            post_overwrites[param].append(i)
    
    # 找所有危险函数调用
    results = []
    
    patterns = [
        r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST)\['(\w+)'\]",
        r"preg_replace\s*\([^)]*\/e[^)]*,\s*\$_(GET|POST)\['(\w+)'\]",
        r"create_function\s*\([^)]*,\s*\$_(GET|POST)\['(\w+)'\]",
        r"call_user_func\s*\([^)]*,\s*\$_(GET|POST)\['(\w+)'\]",
        r"include\s*\(\s*\$_(GET|POST)\['(\w+)'\]",
        r"require\s*\(\s*\$_(GET|POST)\['(\w+)'\]",
    ]
    
    for i, line in enumerate(lines):
        # 跳过注释
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    func, method, param = groups
                else:
                    method, param = groups
                    func = 'preg_replace'
                
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
                overwrites = get_overwrites if method == 'GET' else post_overwrites
                if param in overwrites:
                    # 检查是否有在调用之前的覆盖
                    for ow_line in overwrites[param]:
                        if ow_line < i:
                            # 参数在调用之前被覆盖
                            break
                    else:
                        # 没有在调用之前的覆盖
                        results.append({
                            'file': os.path.basename(filepath),
                            'line': i + 1,
                            'func': func,
                            'method': method,
                            'param': param,
                            'code': line.strip()
                        })
                else:
                    # 参数没有被覆盖
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
    
    print("正在深度分析所有 PHP 文件...")
    for filename in os.listdir(src_dir):
        if filename.endswith('.php'):
            filepath = os.path.join(src_dir, filename)
            shells = analyze_file_detailed(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个可能有效的 shell 入口点\n")
    
    for s in all_shells[:50]:
        print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}'])")
    
    # 保存完整列表
    with open('deep_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")
    
    print(f"\n完整列表已保存到 deep_shells.txt")

if __name__ == '__main__':
    main()
