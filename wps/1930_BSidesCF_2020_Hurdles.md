---
title: "[BSidesCF 2020]Hurdles"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [http-methods, headers, basic-auth, cors, x-forwarded-for, cookie, referer]
vulnerability: HTTP 协议知识挑战，需要按照提示逐步构造正确的 HTTP 请求通过 12 个关卡
solved: true
flag: "flag{d89f4179-bbf1-4080-84c6-89ec17c7dc7b}"
---

# [BSidesCF 2020]Hurdles

## 题目概述
一道 HTTP 协议知识挑战题，需要按照服务端返回的提示逐步构造正确的 HTTP 请求，通过 12 个"障碍"(hurdles)才能获取 flag。

## 信息收集
1. 访问题目首页，提示指明 `/hurdles` 路径
2. 访问 `/hurdles` 返回 401，提示使用 PUT 方法，同时返回 `X-Hurdles-Remaining: 12` 头表示剩余障碍数量
3. 每个 hurdle 会返回下一步需要满足的条件

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：HTTP 协议知识题

**原理**：服务端逐个检查 HTTP 请求的各个属性（方法、路径、查询参数、认证、Headers），每满足一个条件就进入下一关，全部通过后返回 flag。

**判断过程**：
1. 使用 `curl -v` 观察每个响应中的提示文字和 `X-Hurdles-Remaining` 头
2. 根据提示逐步添加所需的请求属性

## 利用过程（Payload + Flag）

**12 个障碍依次通过**：

| Hurdle | 提示 | 解决方式 |
|--------|------|----------|
| 12 | expecting PUT Method | `-X PUT` |
| 11 | path should end in ! | `/hurdles/!` |
| 10 | get the flag in query | `?get=flag` |
| 9 | parameter named &=&=& | `&%26%3D%26%3D%26=%2500%0a` |
| 8 | username player | Basic Auth: `player:` |
| 7 | password = md5("open sesame") | `player:54ef36ec71201fdf9d1423fd26f97f6b` |
| 6 | 1337 Browser, version >9000 | `User-Agent: 1337 Browser v.9999` |
| 5 | forwarded through 127.0.0.1, client 13.37.13.37 | `X-Forwarded-For: 13.37.13.37, 127.0.0.1` |
| 4 | Fortune Cookie with RFC number | `Cookie: Fortune=6265` (RFC 6265) |
| 3 | Accept only plain text | `Accept: text/plain` |
| 2 | speak Russian | `Accept-Language: ru-RU` |
| 1 | share resources with origin | `Origin: https://ctf.bsidessf.net` |
| 0 | be referred by challenges page | `Referer: https://ctf.bsidessf.net/challenges` |

**最终 Payload**：
```bash
# 1. 计算 md5 密码
echo -n "open sesame" | md5sum
# Output: 54ef36ec71201fdf9d1423fd26f97f6b

# 2. 构造完整请求
curl -v -X PUT \
  -u "player:54ef36ec71201fdf9d1423fd26f97f6b" \
  -H "User-Agent: 1337 Browser v.9999" \
  -H "X-Forwarded-For: 13.37.13.37, 127.0.0.1" \
  -H "Cookie: Fortune=6265" \
  -H "Accept: text/plain" \
  -H "Accept-Language: ru-RU" \
  -H "Origin: https://ctf.bsidessf.net" \
  -H "Referer: https://ctf.bsidessf.net/challenges" \
  "http://TARGET/hurdles/!?get=flag&%26%3D%26%3D%26=%2500%0a"
```

**Flag：** `flag{d89f4179-bbf1-4080-84c6-89ec17c7dc7b}`

## 复现步骤
1. 访问题目，发现提示前往 `/hurdles`
2. 使用 PUT 方法访问 `/hurdles`，开始逐关挑战
3. 每次请求后阅读返回的提示文字，添加对应的请求属性
4. 依次通过 12 个关卡，最终在响应头 `X-Ctf-Flag` 中获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| HTTP 协议挑战 | /hurdles 路径 | 构造满足所有条件的 PUT 请求 | HTTP 方法、Basic Auth、Headers、CORS、Cookie |

## 知识总结（解题技巧、同类题型套路）

1. **HTTP 协议知识**：
   - PUT 方法用于资源创建/更新
   - Basic Auth 格式：`Authorization: Basic base64(user:pass)`
   - X-Forwarded-For 可伪造客户端 IP
   - Cookie RFC 6265 是 HTTP State Management Mechanism
   - Origin/Referer 用于 CORS 和来源验证

2. **解题套路**：
   - 仔细阅读每个响应的提示文字
   - 使用 `curl -v` 查看完整的请求/响应头
   - 逐步叠加请求属性，不要跳步
   - 遇到编码问题（如 `%00`、`%26%3D`）使用 curl 直接构造 URL
