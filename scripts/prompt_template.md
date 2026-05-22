你是一个 CTF Web 安全专家。请解以下 CTF 题目。

## 题目信息
- 题目名称：{name}
- 题目 URL：{url}

## 任务

### 第一步：信息收集
用 curl 访问题目页面，分析页面内容和源码，找到解题线索。
把下载的页面/源码保存到 {challenge_dir}/ 目录下。

### 第二步：解题
根据收集到的信息，用 curl/python 与题目交互，找到 flag。

### 第三步：提交 flag
找到 flag 后，用以下命令提交：
```bash
curl -s -X POST "https://buuoj.cn/api/v1/challenges/attempt" \
  -H "Cookie: {cookie}" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -H "CSRF-Token: {csrf}" \
  -d '{{"challenge_id": {cid}, "submission": "你找到的flag"}}'
```
返回 `{{"data":{{"status":"correct"}}}}` 表示成功。失败就继续分析重新找。

### 第四步：撰写 Writeup
提交成功后，直接输出完整 WP（从 --- 开始），格式如下：

---
title: "{name}"
platform: BUUCTF
category: Web
difficulty: 入门/简单/中等/困难
tags: [英文kebab-case标签]
vulnerability: 一句话漏洞描述
solved: true
flag: "flag{{xxxx}}"
---

# {name}

## 题目概述
## 信息收集
## 漏洞分析（漏洞类型、原理、判断过程）
## 利用过程（Payload + Flag）
## 复现步骤
## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）
## 知识总结（解题技巧、同类题型套路）

## 注意事项
- flag 提交成功后才写 WP，失败了就继续解题
- 不要写防御方式
- Payload 干净有注释
- tags 英文小写 kebab-case
- 把解题过程中下载的文件保存到 {challenge_dir}/
- 直接输出 WP 内容，不要尝试写入文件
