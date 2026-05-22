import os
import re

src_dir = '/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src'

results = []

for filename in os.listdir(src_dir):
    if not filename.endswith('.php'):
        continue
    filepath = os.path.join(src_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 逐行分析
        assigned_params = set()  # 已被赋值的参数
        
        for i, line in enumerate(lines):
            # 检查是否有参数赋值
            assign_pattern = r"\$_(GET|POST|REQUEST)\['([^']+)'\]\s*=\s*"
            for match in re.finditer(assign_pattern, line):
                method = match.group(1)
                param = match.group(2)
                assigned_params.add((method, param))
            
            # 检查危险函数调用
            func_pattern = r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST|REQUEST)\['([^']+)'\]"
            for match in re.finditer(func_pattern, line):
                func = match.group(1)
                method = match.group(2)
                param = match.group(3)
                
                # 检查参数是否已被赋值
                if (method, param) not in assigned_params:
                    # 检查这行是否在不可能的条件中
                    # 查找前面的if条件
                    # 简单检查：如果行内有 if('xxx' == 'yyy') 且 xxx != yyy，则跳过
                    
                    # 检查当前行或前面几行是否有不可能的条件
                    context = ''.join(lines[max(0, i-3):i+1])
                    
                    # 检查 if('a' == 'b') 这种不可能条件
                    impossible_if = re.search(r"if\s*\(\s*'([^']+)'\s*==\s*'([^']+)'", context)
                    if impossible_if and impossible_if.group(1) != impossible_if.group(2):
                        continue  # 条件永远为false，跳过
                    
                    results.append((filename, func, method, param, i+1))
    except Exception as e:
        pass

print(f"Found {len(results)} truly exploitable webshells:")
for r in results[:30]:
    print(f"  {r[0]} line {r[4]}: {r[1]}($_{r[2]}['{r[3]}'])")
