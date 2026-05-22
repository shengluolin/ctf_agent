import os
import re

def analyze_file(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        lines = f.readlines()
    
    # Track all dangerous calls and their parameters
    dangerous_patterns = [
        r"echo\s*`\{?\$_GET\['([^']+)'\]}\?`",  # backtick
        r"(system|exec|shell_exec|passthru)\s*\(\s*\$_GET\['([^']+)'\]",  # system/exec
        r"eval\s*\(\s*\$_GET\['([^']+)'\]",  # eval
        r"assert\s*\(\s*\$_GET\['([^']+)'\]",  # assert
    ]
    
    results = []
    
    for i, line in enumerate(lines):
        for pattern in dangerous_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                param = match if isinstance(match, str) else match[-1]
                
                # Check if this parameter is overwritten before this line
                is_overwritten = False
                for j in range(i):
                    prev_line = lines[j]
                    # Check if parameter is set to empty or fixed value
                    if re.search(rf"\$_GET\['{param}'\]\s*=\s*['\"]", prev_line):
                        is_overwritten = True
                        break
                
                # Check if line is inside false condition
                is_dead = False
                if re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", line):
                    match = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\)", line)
                    if match.group(1) != match.group(2):
                        is_dead = True
                
                if not is_overwritten and not is_dead:
                    results.append((filepath, i+1, param, line.strip()))
    
    return results

all_results = []
for filename in os.listdir('src'):
    if filename.endswith('.php'):
        filepath = os.path.join('src', filename)
        results = analyze_file(filepath)
        all_results.extend(results)

print(f"Found {len(all_results)} potentially working backdoors:")
for filepath, line_num, param, line in all_results[:50]:
    print(f"{filepath}:{line_num} param={param}")
    print(f"  {line[:80]}")
