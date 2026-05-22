import os
import re

src_dir = '/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src'

# 模式：危险函数调用，参数来自用户输入
# 格式：function($_GET['param'] ?? 'default')
func_pattern = r"(eval|system|exec|shell_exec|passthru|assert)\s*\(\s*\$_(GET|POST|REQUEST)\['([^']+)'\]"

results = []

for filename in os.listdir(src_dir):
    if not filename.endswith('.php'):
        continue
    filepath = os.path.join(src_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 找所有危险函数调用
        for match in re.finditer(func_pattern, content):
            func = match.group(1)
            method = match.group(2)
            param = match.group(3)
            
            # 检查这个参数是否在函数调用之前被赋值
            # 找到函数调用的位置
            call_pos = match.start()
            
            # 查找 $_GET['param'] = 'xxx' 这样的赋值
            # 注意：需要在函数调用之前
            override_pattern = r"\$_" + method + r"\['" + re.escape(param) + r"'\]\s*=\s*"
            override_matches = list(re.finditer(override_pattern, content))
            
            # 检查是否有在调用之前的赋值
            has_override_before = False
            for om in override_matches:
                if om.start() < call_pos:
                    has_override_before = True
                    break
            
            if not has_override_before:
                results.append((filename, func, method, param))
    except Exception as e:
        pass

print(f"Found {len(results)} potential exploitable webshells (no override before call):")
for r in results[:100]:
    print(f"  {r[0]}: {r[1]}($_{r[2]}['{r[3]}'])")
