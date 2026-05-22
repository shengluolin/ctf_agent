---
title: "[BSidesCF 2019]Futurella"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [source-code-disclosure, html-comment]
vulnerability: Flag 直接暴露在页面源码中
solved: true
flag: "flag{a2cbf78f-91df-4579-9ae5-8aa18fe34499}"
---

# [BSidesCF 2019]Futurella

## 题目概述
题目是一个关于外星人入侵的简单网页，提示"我们在垃圾桶里发现了这张纸条，我们认为这是入侵的外星人留下的！你能读懂吗？"

## 信息收集
使用 curl 访问题目页面，直接查看 HTML 源码：

```bash
curl -s "http://target-url/"
```

## 漏洞分析（漏洞类型、原理、判断过程）
这是一道入门级题目，没有真正的漏洞。Flag 直接写在 HTML 源码中：

```html
<div class='challenge rounded'>
  <p>Resistance is futile! Bring back Futurella or we'll invade!</p>
  <p>Also, the flag is flag{a2cbf78f-91df-4579-9ae5-8aa18fe34499}</p>
</div>
```

题目可能试图误导解题者去"解密"外星人的信息，但实际上 flag 就在页面源码里。

## 利用过程（Payload + Flag）
无需任何 payload，直接查看页面源码即可获得 flag：

```bash
curl -s "http://target-url/" | grep flag
```

**Flag:** `flag{a2cbf78f-91df-4579-9ae5-8aa18fe34499}`

## 复现步骤
1. 访问题目 URL
2. 查看页面源码（Ctrl+U 或 curl）
3. 搜索 "flag" 关键字
4. 获得 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 信息泄露 | 页面源码 | 无 | 源码审计 |

## 知识总结（解题技巧、同类题型套路）
- **解题技巧**：做 Web 题时，养成先查看页面源码的习惯，不要只看浏览器渲染后的内容
- **同类题型套路**：入门级 CTF 题目常把 flag 隐藏在源码、注释、HTTP 响应头等地方，优先检查这些位置
