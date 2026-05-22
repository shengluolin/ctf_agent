import os
import re

dangerous_patterns = [
    (r'eval\(\$_GET\[\'([^\']+)\'\]', 'eval', 'GET'),
    (r'eval\(\$_POST\[\'([^\']+)\'\]', 'eval', 'POST'),
    (r'system\(\$_GET\[\'([^\']+)\'\]', 'system', 'GET'),
    (r'system\(\$_POST\[\'([^\']+)\'\]', 'system', 'POST'),
    (r'exec\(\$_GET\[\'([^\']+)\'\]', 'exec', 'GET'),
    (r'exec\(\$_POST\[\'([^\']+)\'\]', 'exec', 'POST'),
    (r'assert\(\$_GET\[\'([^\']+)\'\]', 'assert', 'GET'),
    (r'assert\(\$_POST\[\'([^\']+)\'\]', 'assert', 'POST'),
    (r'passthru\(\$_GET\[\'([^\']+)\'\]', 'passthru', 'GET'),
    (r'passthru\(\$_POST\[\'([^\']+)\'\]', 'passthru', 'POST'),
]

real_shells = []

for filename in sorted(os.listdir('.')):
    if not filename.endswith('.php'):
        continue
    
    with open(filename, 'r', errors='ignore') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find function boundaries
    function_ranges = []
    in_function = False
    brace_count = 0
    func_start = 0
    
    for i, line in enumerate(lines):
        if re.match(r'^\s*function\s+\w+\s*\(', line):
            in_function = True
            func_start = i
            brace_count = line.count('{') - line.count('}')
        elif in_function:
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0:
                function_ranges.append((func_start, i))
                in_function = False
    
    def is_inside_function(line_num):
        for start, end in function_ranges:
            if start <= line_num <= end:
                return True
        return False
    
    for pattern, func_name, method in dangerous_patterns:
        for match in re.finditer(pattern, content):
            param_name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            
            line_content = lines[line_num - 1].strip()
            
            if not line_content.startswith(func_name + '($_'):
                continue
            
            call_in_func = is_inside_function(line_num - 1)
            
            # Check for overwrite in the SAME scope (inside or outside function)
            overwrite_pattern = r'\$_' + method + r'\[\'' + re.escape(param_name) + r'\'\]\s*='
            
            # Get content before this line in the same scope
            if call_in_func:
                # Find the function start
                for start, end in function_ranges:
                    if start <= line_num - 1 <= end:
                        before_content = '\n'.join(lines[start:line_num-1])
                        break
            else:
                # Outside functions - check all lines before that are also outside functions
                outside_lines = []
                for i in range(line_num - 1):
                    if not is_inside_function(i):
                        outside_lines.append(lines[i])
                before_content = '\n'.join(outside_lines)
            
            has_overwrite = bool(re.search(overwrite_pattern, before_content))
            
            # Check for if condition in previous 3 lines
            prev_3 = '\n'.join(lines[max(0, line_num-3):line_num])
            has_if = bool(re.search(r"if\s*\(['\"]+[^'\"]+['\"]+\s*==\s*['\"]+[^'\"]+['\"]+\)", prev_3))
            
            if not has_overwrite and not has_if:
                real_shells.append({
                    'file': filename,
                    'line': line_num,
                    'func': func_name,
                    'param': param_name,
                    'method': method,
                    'code': line_content,
                    'in_func': call_in_func
                })

print(f"Found {len(real_shells)} REAL shells (considering scope):\n")
for s in real_shells[:50]:
    print(f"{s['file']}:{s['line']} - {s['func']}({s['method']}['{s['param']}']) - in_func: {s['in_func']}")
