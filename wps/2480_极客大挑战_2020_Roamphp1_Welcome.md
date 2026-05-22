---
title: "[极客大挑战 2020]Roamphp1-Welcome"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [php, sha1-bypass, weak-type-comparison, array-bypass, phpinfo]
vulnerability: PHP 弱类型比较绕过，利用数组使 sha1() 返回 NULL 实现绕过
solved: true
flag: "flag{466dd567-29f2-4e64-be0d-52963d0df217}"
---

# [极客大挑战 2020]Roamphp1-Welcome

## 题目概述
一道 PHP 弱类型比较绕过题目，需要通过数组绕过 sha1() 函数的比较，从而触发 phpinfo() 获取 flag。

## 信息收集
1. 访问题目 URL，返回 `405 Method Not Allowed`
2. 尝试 POST 请求，获得 PHP 源码：
```php
<?php
error_reporting(0);
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header("HTTP/1.1 405 Method Not Allowed");
    exit();
} else {
    if (!isset($_POST['roam1']) || !isset($_POST['roam2'])){
        show_source(__FILE__);
    }
    else if ($_POST['roam1'] !== $_POST['roam2'] && sha1($_POST['roam1']) === sha1($_POST['roam2'])){
        phpinfo();  // collect information from phpinfo!
    }
}
```

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP 弱类型比较 + 数组绕过

**原理**：
- PHP 中 `sha1()` 函数无法处理数组类型，当传入数组时会返回 `NULL`
- 因此 `sha1(array()) === sha1(array())` 实际上是 `NULL === NULL`，结果为 `true`
- 同时两个不同的数组 `roam1[]=1` 和 `roam2[]=2` 满足 `roam1 !== roam2` 的条件

**判断过程**：
- 代码要求 `roam1 !== roam2` 且 `sha1(roam1) === sha1(roam2)`
- 正常字符串无法满足此条件（sha1 碰撞极难）
- 利用 PHP 数组特性绕过 sha1 比较

## 利用过程（Payload + Flag）

**Payload**：
```bash
curl -X POST "http://target/" -d "roam1[]=1&roam2[]=2"
```

**原理说明**：
- `roam1[]=1` → PHP 解析为 `$_POST['roam1'] = array(1)`
- `roam2[]=2` → PHP 解析为 `$_POST['roam2'] = array(2)`
- 两个数组不同，满足 `roam1 !== roam2`
- `sha1(array())` 返回 NULL，满足 `sha1(roam1) === sha1(roam2)`

**获取 Flag**：
触发 phpinfo() 后，在 PHP Variables 中找到 FLAG 环境变量：
```
FLAG: flag{466dd567-29f2-4e64-be0d-52963d0df217}
```

## 复现步骤
1. 访问题目，发现 405 错误
2. 改用 POST 请求，获取源码
3. 分析代码逻辑，发现需要绕过 sha1 严格比较
4. 构造数组参数 `roam1[]=1&roam2[]=2` 绕过
5. 在 phpinfo 页面中搜索 FLAG 找到 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 弱类型比较 | POST 参数 roam1/roam2 | `roam1[]=1&roam2[]=2` | sha1() 处理数组返回 NULL |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
- 遇到 `md5()` 或 `sha1()` 比较时，优先考虑数组绕过
- `md5(array())` 和 `sha1(array())` 都返回 NULL

**同类题型套路**：
1. `md5($a) === md5($b)` 且 `$a !== $b` → 数组绕过
2. `sha1($a) === sha1($b)` 且 `$a !== $b` → 数组绕过
3. `md5($a) == md5($b)` → 可用弱类型绕过（如 `0e` 开头的科学计数法）
4. 常见弱比较字符串：`240610708` 和 `QNKCDZO` 的 md5 值都是 `0e` 开头
