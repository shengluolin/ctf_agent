---
title: "[FireshellCTF2020]Caas"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [c-compiler, include-directive, file-read, error-message-leak]
vulnerability: C预处理器#include指令可读取任意文件，编译错误信息泄露文件内容
solved: true
flag: "flag{0f532fd4-8d62-44ed-bbc2-45e51fed1f7d}"
---

# [FireshellCTF2020]Caas

## 题目概述
题目是一个 CaaS (Compiler as a Service) 服务，允许用户提交 C 代码进行编译，返回编译后的 ELF 二进制文件或编译错误信息。

## 信息收集
访问页面发现是一个 C 代码编译服务，表单提交代码后服务器编译并返回结果。测试提交正常 C 代码会返回编译后的 ELF 二进制文件。

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**: C预处理器文件读取 + 编译错误信息泄露

**原理**: C语言的 `#include` 预处理指令会将指定文件的内容插入到源代码中。当包含一个非 C 代码格式的文件（如 `/flag`）时，编译器会报错并在错误信息中显示文件内容。

**判断过程**: 
1. 服务接受 C 代码并编译
2. C预处理器会处理 `#include` 指令
3. 编译失败时错误信息会回显给用户
4. 错误信息中包含被包含文件的内容片段

## 利用过程（Payload + Flag）
**Payload**:
```c
#include "/flag"
```

提交上述代码，服务器尝试编译，预处理器读取 `/flag` 文件内容插入源码，因 flag 内容不符合 C 语法导致编译错误，错误信息中泄露 flag。

**错误信息输出**:
```
/flag:1:5: error: expected '=', ',', ';', 'asm' or '__attribute__' before '{' token
 flag{0f532fd4-8d62-44ed-bbc2-45e51fed1f7d}
     ^
```

**Flag**: `flag{0f532fd4-8d62-44ed-bbc2-45e51fed1f7d}`

## 复现步骤
1. 访题目 URL
2. 在代码框输入 `#include "/flag"`
3. 点击 Compile 按钮
4. 在返回的错误信息中找到 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心Payload | 知识点 |
|---------|---------|------------|--------|
| 预处理器文件读取 | C代码编译服务 | `#include "/flag"` | C预处理器工作原理 |
| 信息泄露 | 编译错误回显 | - | 编译器错误信息格式 |

## 知识总结（解题技巧、同类题型套路）
- **解题技巧**: 当遇到代码编译/执行服务时，考虑利用语言特性读取敏感文件
- **C语言特性**: `#include` 可以包含任意路径的文件，不限于 `.h` 文件
- **同类题型**: 类似思路可用于其他编译服务（如 GCC、Clang）或解释型语言中利用文件读取函数
- **扩展**: 可尝试读取 `/etc/passwd`、环境变量文件、源码文件等其他敏感信息
