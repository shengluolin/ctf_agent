#!/usr/bin/env python3
import os
import re

def analyze_file(filepath):
    """分析变量流，找出从参数到危险函数的路径"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # 记录变量来源
    var_sources = {}  # var_name -> (source_type, source_param, line)
    
    for i, line in enumerate(lines):
        # 匹配 $var = $_GET['xxx'] 或 $var = $_POST['xxx']
        get_match = re.search(r'\$(\w+)\s*=\s*\$_GET\[\'(\w+)\'\]', line)
        post_match = re.search(r'\$(\w+)\s*=\s*\$_POST\[\'(\w+)\'\]', line)
        
        if get_match:
            var_name, param = get_match.groups()
            var_sources[var_name] = ('GET', param, i)
        if post_match:
            var_name, param = post_match.groups()
            var_sources[var_name] = ('POST', param, i)
    
    # 检查危险函数调用中使用变量
    results = []
    
    for i, line in enumerate(lines):
        # 匹配 eval($var), system($var), exec($var), etc.
        match = re.search(r'(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$(\w+)\s*\)', line)
        if match:
            func, var_name = match.groups()
            
            # 检查变量是否来自参数
            if var_name in var_sources:
                source_type, source_param, source_line = var_sources[var_name]
                
                # 检查变量赋值是否在调用之前
                if source_line < i:
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
                    
                    if not is_fake:
                        results.append({
                            'file': os.path.basename(filepath),
                            'line': i + 1,
                            'func': func,
                            'method': source_type,
                            'param': source_param,
                            'var': var_name,
                            'source_line': source_line + 1
                        })
    
    return results

def main():
    src_dir = 'src'
    all_shells = []
    
    print("正在追踪变量流...")
    for filename in os.listdir(src_dir):
        if filename.endswith('.php'):
            filepath = os.path.join(src_dir, filename)
            shells = analyze_file(filepath)
            all_shells.extend(shells)
    
    print(f"\n找到 {len(all_shells)} 个变量流 shell 入口点\n")
    
    for s in all_shells[:50]:
        print(f"{s['file']}:{s['line']} - {s['func']}(${s['var']}) <- {s['method']}['{s['param']}'] (line {s['source_line']})")
    
    with open('var_flow_shells.txt', 'w') as f:
        for s in all_shells:
            f.write(f"{s['file']}:{s['line']}:{s['func']}:{s['method']}:{s['param']}\n")

if __name__ == '__main__':
    main()
