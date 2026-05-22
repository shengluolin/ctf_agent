---
title: "[MRCTF2020]PYWebsite"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [ip-spoofing, x-forwarded-for, access-control-bypass]
vulnerability: 服务端通过 X-Forwarded-For 头进行 IP 验证，可被伪造绕过
solved: true
flag: "flag{921df965-a5b9-4335-be71-57f791b70093}"
---

# [MRCTF2020]PYWebsite

## 题目概述
一个模拟"购买Flag"的网站，需要输入授权码才能获取Flag。页面提示"PY or NvZhuang to Get it"，暗示可以通过某种方式绕过验证。

## 信息收集
1. 访问首页，发现验证逻辑在前端 JavaScript 中：
   - 使用 MD5 验证授权码
   - 验证通过后跳转到 `./flag.php`
2. 直接访问 `flag.php` 返回提示："我已经把购买者的IP保存了，显然你没有购买"
3. 提示"验证逻辑是在后端的，除了购买者和我自己，没有人可以看到flag"

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：IP 伪造绕过

**原理**：
- 服务端通过检查 `X-Forwarded-For` 请求头来判断客户端 IP
- `X-Forwarded-For` 是一个可被客户端伪造的请求头
- 当服务器直接信任此头部而不进行验证时，攻击者可以伪造任意 IP

**判断过程**：
1. 页面提示"购买者IP保存"→ IP 验证机制
2. 题目提示"PY"→ 朋友/伪造
3. 尝试常见 IP 伪造头部：`X-Forwarded-For`、`Client-IP`、`X-Real-IP`
4. `X-Forwarded-For: 127.0.0.1` 成功绕过

## 利用过程（Payload + Flag）

```bash
# 直接访问被拦截
curl -s "http://target/flag.php"
# 返回：拜托，我也是学过半小时网络安全的，你骗不了我！

# 添加 X-Forwarded-For 头伪造本地 IP
curl -s "http://target/flag.php" -H "X-Forwarded-For: 127.0.0.1"
# 返回：flag{921df965-a5b9-4335-be71-57f791b70093}
```

## 复现步骤
1. 访问题目首页，分析前端验证逻辑
2. 直接访问 `flag.php`，发现需要 IP 验证
3. 添加 `X-Forwarded-For: 127.0.0.1` 请求头
4. 成功获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| IP伪造绕过 | flag.php | `X-Forwarded-For: 127.0.0.1` | HTTP头部可伪造性 |

## 知识总结（解题技巧、同类题型套路）
1. **IP伪造头部优先级**：`X-Forwarded-For` > `Client-IP` > `X-Real-IP` > `X-Originating-IP`
2. **常见绕过场景**：IP限制、地域限制、管理员访问限制
3. **题目暗示**：题目中的"PY"暗示伪造/欺骗，中文谐音提示
