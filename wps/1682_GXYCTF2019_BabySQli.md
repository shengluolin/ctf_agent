---
title: "[GXYCTF2019]BabySQli"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sql-injection, union-injection, authentication-bypass, base32-encoding, md5-password]
vulnerability: SQL注入联合查询绕过登录认证
solved: true
flag: "flag{f7bcc9f6-9044-45b5-9a62-c994353833c5}"
---

# [GXYCTF2019]BabySQli

## 题目概述
题目是一个登录页面，需要输入用户名和密码。页面标题为 "Do you know who am I?"，表单提交到 search.php。

## 信息收集
1. 访问首页，发现登录表单
2. 查看页面源码，发现隐藏的 Base32 编码注释：`MMZFM422K5HDASKDN5TVU3SKOZRFGQRRMMZFM6KJJBSG6WSYJJWESSCWPJNFQSTVLFLTC3CJIQYGOSTZKJ2VSVZRNRFHOPJ5`
3. 解码过程：
   - Base32 解码得到：`c2VsZWN0ICogZnJvbSB1c2VyIHdoZXJlIHVzZXJuYW1lID0gJyRuYW1lJw==`
   - Base64 解码得到：`select * from user where username = '$name'`
4. 测试发现存在 SQL 注入，错误信息显示为 MySQL 数据库

## 漏洞分析（漏洞类型、原理、判断过程）
**漏洞类型**：SQL注入（联合查询注入）

**原理**：
- 后端 SQL 查询语句为 `select * from user where username = '$name'`
- 参数未经过滤直接拼接到 SQL 语句中
- 密码验证逻辑：将用户输入的密码进行 MD5 加密后与数据库中的密码比对
- 表结构为 3 列：id, username, password

**判断过程**：
1. 输入 `admin'` 触发 SQL 语法错误，确认存在注入点
2. 测试 `order by` 被 WAF 拦截（返回 "do not hack me!"）
3. 测试 `union select 1,2,3` 成功执行
4. 通过测试确定列顺序：第2列为 username，第3列为 password
5. 密码使用 MD5 存储

## 利用过程（Payload + Flag）

**最终 Payload**：
```
name=0' union select 1,'admin','202cb962ac59075b964b07152d234b70'#&pw=123
```

**解释**：
- `0'` 使原查询返回空结果
- `union select 1,'admin','202cb962ac59075b964b07152d234b70'` 构造虚拟用户数据
- 第2列填入 `admin` 作为用户名
- 第3列填入 `123` 的 MD5 值 `202cb962ac59075b964b07152d234b70`
- 密码参数 `pw=123` 会被 MD5 加密后与数据库中的值比对
- 两者匹配后成功登录，返回 flag

**Flag**: `flag{f7bcc9f6-9044-45b5-9a62-c994353833c5}`

## 复现步骤
1. 访问题目 URL
2. 查看页面源码，发现 Base32 编码的注释
3. 双重解码得到 SQL 查询语句
4. 测试 SQL 注入点
5. 使用联合注入构造虚拟用户数据
6. 密码使用 MD5 值绕过验证

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| SQL注入 | 用户名参数 | `union select 1,'admin',md5_hash#` | 联合注入、MD5密码绕过 |

## 知识总结
1. **编码识别**：注意页面源码中的隐藏注释，Base32 编码特征为大写字母和数字
2. **联合注入绕过登录**：当无法获取真实密码时，可通过 union select 构造虚拟数据绕过
3. **密码加密处理**：登录系统常对密码进行 MD5 加密后比对，注入时需提供 MD5 值
4. **列顺序探测**：通过观察返回信息判断哪一列对应用户名/密码
