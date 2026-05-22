---
title: "[b01lers2020]Welcome to Earth"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [javascript-audit, source-code-review, client-side-bypass]
vulnerability: 客户端验证可被绕过，关键信息泄露在 JavaScript 源码中
solved: true
flag: "pctf{hey_boys_im_baaaaaaaaaack!}"
---

# [b01lers2020]Welcome to Earth

## 题目概述
这是一道 JavaScript 源码审计题，模拟了一个外星人入侵地球的故事场景。玩家需要通过分析前端 JavaScript 代码，找到隐藏的路径和打乱的 flag 片段。

## 信息收集
1. 访问首页，发现 JavaScript 逻辑：按 ESC 键跳转到 `/chase/`，否则 10 秒后跳转到 `/die/`
2. 访问 `/chase/`，发现隐藏函数 `leftt()` 指向 `/leftt/`（注意两个 t）
3. 访问 `/leftt/`，HTML 注释中隐藏了 `/shoot/` 路径
4. 访问 `/shoot/` → `/door/` → `/open/` → `/fight/`
5. 在 `/fight/` 页面的 `fight.js` 中找到打乱的 flag 片段

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：客户端验证绕过 + 敏感信息泄露
- **原理**：
  1. 所有路径跳转逻辑都在前端 JavaScript 中实现，可直接访问目标 URL 绕过交互
  2. `/door/` 页面的随机数验证在客户端执行，可直接访问 `/open/`
  3. `/open/` 页面的递归计数器需要执行 40 亿次，但可直接访问 `/fight/`
  4. flag 片段直接硬编码在 JavaScript 文件中

## 利用过程（Payload + Flag）
1. 审计首页 JS，发现 `/chase/` 路径
2. 审计 `/chase/` 页面 JS，发现隐藏的 `leftt()` 函数指向 `/leftt/`
3. 查看 `/leftt/` HTML 源码，在注释中发现 `/shoot/` 路径
4. 依次访问 `/shoot/` → `/door/` → `/open/` → `/fight/`
5. 分析 `/static/js/fight.js`，获取 flag 片段：
   ```javascript
   var flag = ["{hey", "_boy", "aaaa", "s_im", "ck!}", "_baa", "aaaa", "pctf"];
   ```
6. 还原 flag：`pctf{hey_boys_im_baaaaaaaaaack!}`

## 复现步骤
```bash
# 1. 访问首页
curl -s "http://target/"

# 2. 分析 JS 后直接访问关键路径
curl -s "http://target/chase/"
curl -s "http://target/leftt/"
curl -s "http://target/shoot/"
curl -s "http://target/door/"
curl -s "http://target/open/"
curl -s "http://target/fight/"

# 3. 获取 flag 片段
curl -s "http://target/static/js/fight.js"

# 4. 还原 flag: pctf{hey_boys_im_baaaaaaaaaack!}
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）
| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| 客户端验证绕过 | JavaScript 跳转逻辑 | 直接访问目标 URL | 前端验证不可信 |
| 信息泄露 | JS 文件、HTML 注释 | 查看源码获取隐藏路径 | 源码审计 |
| 逻辑隐藏 | 函数命名混淆 | `leftt()` vs `left()` | 代码审计技巧 |

## 知识总结（解题技巧、同类题型套路）
1. **JavaScript 审计套路**：
   - 查看所有外部 JS 文件
   - 搜索隐藏函数和注释代码
   - 分析跳转逻辑，直接访问目标 URL

2. **常见隐藏方式**：
   - HTML 注释隐藏真实按钮/链接
   - JavaScript 函数命名混淆（如 `leftt` vs `left`）
   - 客户端验证可被绕过

3. **Flag 片段还原技巧**：
   - 识别 flag 格式前缀（如 `pctf`）
   - 识别结尾标志（如 `}`）
   - 根据语义拼接有意义的短语
