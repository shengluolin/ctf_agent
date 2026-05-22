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
            content = f.read()
        
        # 找所有危险函数调用
        # 模式：system($_GET['xxx'] ?? ' ') 或 eval($_GET['xxx'] ?? ' ')
        func_pattern = r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST|REQUEST)\['([^']+)'\]\s*\?\?\s*'[^']*'\s*\)"
        
        for match in re.finditer(func_pattern, content):
            func = match.group(1)
            method = match.group(2)
            param = match.group(3)
            call_pos = match.start()
            
            # 检查是否有 $_GET['param'] = 'xxx' 赋值
            # 关键：赋值必须在函数调用之前
            override_pattern = r"\$_" + method + r"\['" + re.escape(param) + r"'\]\s*=\s*"
            
            # 找所有赋值位置
            for override_match in re.finditer(override_pattern, content):
                if override_match.start() < call_pos:
                    # 这个参数在调用之前被覆盖了，跳过
                    break
            else:
                # 没有找到在调用之前的赋值，这是一个可利用的webshell
                results.append((filename, func, method, param))
    except Exception as e:
        pass

print(f"Found {len(results)} truly exploitable webshells:")
for r in results[:50]:
    print(f"  {r[0]}: {r[1]}($_{r[2]}['{r[3]}'])")
