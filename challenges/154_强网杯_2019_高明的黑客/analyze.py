import os
import re

# 危险函数列表
dangerous_functions = [
    r'eval\s*\(\s*\$_GET',
    r'eval\s*\(\s*\$_POST',
    r'eval\s*\(\s*\$_REQUEST',
    r'system\s*\(\s*\$_GET',
    r'system\s*\(\s*\$_POST',
    r'system\s*\(\s*\$_REQUEST',
    r'exec\s*\(\s*\$_GET',
    r'exec\s*\(\s*\$_POST',
    r'shell_exec\s*\(\s*\$_GET',
    r'shell_exec\s*\(\s*\$_POST',
    r'passthru\s*\(\s*\$_GET',
    r'passthru\s*\(\s*\$_POST',
    r'assert\s*\(\s*\$_GET',
    r'assert\s*\(\s*\$_POST',
    r'preg_replace\s*\([^)]*\/[a-z]*e[a-z]*[\'"].*\$_GET',
    r'create_function\s*\([^)]*\$_GET',
    r'create_function\s*\([^)]*\$_POST',
]

# 更通用的模式 - 查找用户输入直接进入危险函数
patterns = [
    # eval($_GET['xxx'] ?? ' ') 模式
    (r'eval\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'eval'),
    (r'eval\s*\(\s*\$_POST\[\'([^\']+)\'\]', 'eval'),
    (r'eval\s*\(\s*\$_REQUEST\[\'([^\']+)\'\]', 'eval'),
    # system($_GET['xxx'] ?? ' ') 模式
    (r'system\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'system'),
    (r'system\s*\(\s*\$_POST\[\'([^\']+)\'\]', 'system'),
    # assert
    (r'assert\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'assert'),
    (r'assert\s*\(\s*\$_POST\[\'([^\']+)\'\]', 'assert'),
    # exec
    (r'exec\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'exec'),
    # shell_exec
    (r'shell_exec\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'shell_exec'),
    # passthru
    (r'passthru\s*\(\s*\$_GET\[\'([^\']+)\'\]', 'passthru'),
]

results = []
src_dir = '/home/lls/data/ctf-agent/challenges/154_强网杯_2019_高明的黑客/src'

for filename in os.listdir(src_dir):
    if not filename.endswith('.php'):
        continue
    filepath = os.path.join(src_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        for pattern, func in patterns:
            matches = re.findall(pattern, content)
            for param in matches:
                # 检查这个参数是否在前面被覆盖
                # 查找 $_GET['param'] = 'xxx' 这样的赋值
                override_pattern = r"\$_GET\[\'" + re.escape(param) + r"\'\]\s*=\s*[^;]+;"
                if not re.search(override_pattern, content):
                    results.append((filename, func, 'GET', param))
    except Exception as e:
        pass

print(f"Found {len(results)} potential webshells:")
for r in results[:50]:
    print(f"  {r[0]}: {r[1]}($_{r[2]}['{r[3]}'])")
