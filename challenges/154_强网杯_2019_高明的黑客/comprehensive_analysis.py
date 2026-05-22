import os
import re

def analyze_php_file(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        lines = f.readlines()
    
    results = []
    
    # Track which parameters are overwritten
    overwritten_params = set()
    
    # Track brace depth to know if we're inside a false condition block
    brace_depth = 0
    in_false_block = False
    false_block_depth = 0
    
    for i, line in enumerate(lines):
        # Track braces
        open_braces = line.count('{')
        close_braces = line.count('}')
        
        # Check for false condition start
        false_cond = re.search(r"if\s*\(['\"]([^'\"]+)['\"]\s*==\s*['\"]([^'\"]+)['\"]\s*\)\s*\{?", line)
        if false_cond:
            str1, str2 = false_cond.groups()
            if str1 != str2:
                in_false_block = True
                false_block_depth = brace_depth
        
        # Update brace depth
        brace_depth += open_braces - close_braces
        
        # Check if we exited a false block
        if in_false_block and brace_depth <= false_block_depth:
            in_false_block = False
        
        # Track parameter overwrites
        overwrite = re.search(r"\$_GET\['([^']+)'\]\s*=\s*['\"]", line)
        if overwrite:
            overwritten_params.add(overwrite.group(1))
        
        # Skip if in false block
        if in_false_block:
            continue
        
        # Look for dangerous calls with $_GET directly
        direct_call = re.search(r"(system|exec|shell_exec|passthru)\s*\(\s*\$_GET\['([^']+)'\]", line)
        if direct_call:
            func, param = direct_call.groups()
            if param not in overwritten_params:
                results.append((i+1, 'direct', func, param, line.strip()))
        
        # Look for backtick with $_GET
        backtick = re.search(r"echo\s*`\{?\$_GET\['([^']+)'\]}\?`", line)
        if backtick:
            param = backtick.group(1)
            if param not in overwritten_params:
                results.append((i+1, 'backtick', 'backtick', param, line.strip()))
        
        # Look for eval/assert with $_GET
        eval_call = re.search(r"(eval|assert)\s*\(\s*\$_GET\['([^']+)'\]", line)
        if eval_call:
            func, param = eval_call.groups()
            if param not in overwritten_params:
                results.append((i+1, 'eval', func, param, line.strip()))
    
    return results

all_results = []
for filename in sorted(os.listdir('src')):
    if filename.endswith('.php'):
        filepath = os.path.join('src', filename)
        results = analyze_php_file(filepath)
        for r in results:
            all_results.append((filename, r[0], r[1], r[2], r[3], r[4]))

print(f"Found {len(all_results)} potentially working backdoors:")
for filename, line_num, type_, func, param, line in all_results[:50]:
    print(f"{filename}:{line_num} {func}($_GET['{param}'])")
