---
title: "[MRCTF2020]Ez_bypass"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [php, md5-bypass, type-juggling, weak-comparison]
vulnerability: PHP 弱类型比较与 MD5 数组绕过
solved: true
flag: "flag{bb3495d1-bb6b-4f09-8c72-8685432c0111}"
---

# [MRCTF2020]Ez_bypass

## 题目概述
题目是一个 PHP 代码审计题，页面源码直接暴露在 F12 中。需要绕过两层验证才能获取 flag。

## 信息收集
访问题目 URL，页面提示查看 F12，直接返回了 PHP 源码：
- 包含 `flag.php` 文件
- 需要通过两个条件判断才能 `highlight_file('flag.php')`

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞一：MD5 严格比较绕过
```php
if (md5($id) === md5($gg) && $id !== $gg)
```
- 使用 `===` 严格比较 MD5 值
- 要求 `$id !== $gg`（值不同）

**绕过方法**：PHP 中 `md5()` 函数无法处理数组，传入数组会返回 `NULL`，两个 `NULL === NULL` 为 `true`，而两个不同数组值也不相等。

### 漏洞二：弱类型比较绕过
```php
if (!is_numeric($passwd)) {
    if($passwd==1234567) {
        // get flag
    }
}
```
- `is_numeric()` 检查是否为数字
- `==` 弱比较要求等于 `1234567`

**绕过方法**：`is_numeric("1234567a")` 返回 `false`（非纯数字），但 `"1234567a" == 1234567` 弱比较时字符串会被转换为数字 `1234567`，比较成立。

## 利用过程（Payload + Flag）

```bash
# 完整 Payload
curl -s "http://target/?gg[]=1&id[]=2" -X POST -d "passwd=1234567a"
```

**解释**：
- `?gg[]=1&id[]=2`：GET 传数组，`md5(array)` 返回 NULL，绕过 MD5 严格比较
- `passwd=1234567a`：POST 传字符串，绕过 `is_numeric()` 同时满足弱比较

**Flag**：`flag{bb3495d1-bb6b-4f09-8c72-8685432c0111}`

## 复现步骤
1. 访问题目页面，F12 查看源码
2. 分析 PHP 代码逻辑，发现两层绕过
3. 构造 GET 参数：`gg[]=1&id[]=2`（数组绕过 MD5）
4. 构造 POST 参数：`passwd=1234567a`（弱类型绕过）
5. 获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| MD5 数组绕过 | GET 参数 | `gg[]=1&id[]=2` | PHP md5() 处理数组返回 NULL |
| 弱类型比较 | POST 参数 | `passwd=1234567a` | is_numeric() 与 == 弱比较差异 |

## 知识总结（解题技巧、同类题型套路）

1. **PHP 弱类型比较套路**：
   - `==` 比较时会进行类型转换
   - 字符串与数字比较时，字符串开头数字部分会被提取
   - `"123abc" == 123` 为 `true`

2. **MD5 绕过套路**：
   - 严格比较 `===`：使用数组绕过（`md5(array)` 返回 NULL）
   - 弱比较 `==`：可使用 MD5 碰撞字符串（如 `QNKCDZO`、`240610708`）

3. **is_numeric() 绕过**：
   - 只接受纯数字字符串
   - 后缀加字母即可绕过：`123a`、`123.45e1` 等
