#!/usr/bin/env python3
import subprocess
import requests
import re

charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def get_prefix_and_session():
    """获取前缀字符串和session"""
    session = requests.Session()
    resp = session.get("http://b644583a-05a9-4dbf-8264-e9e41c1dd2ff.node5.buuoj.cn:81/check.php")
    match = re.search(r"<p id='p1'>([^<]+)</p>", resp.text)
    if match:
        return match.group(1), session
    return None, None

def prefix_to_args(prefix):
    """将前缀转换为php_mt_seed参数"""
    args = []
    for c in prefix:
        pos = charset.index(c)
        args.extend([str(pos), str(pos), "0", "61"])
    return args

def crack_seed(args):
    """使用php_mt_seed破解种子"""
    cmd = ["/home/lls/data/ctf-agent/tools/php_mt_seed/php_mt_seed"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    # 查找 PHP 7.1.0+ 的种子
    match = re.search(r'seed = 0x[0-9a-f]+ = (\d+) \(PHP 7\.1\.0\+\)', result.stdout)
    if match:
        return int(match.group(1))
    return None

def generate_full_string(seed):
    """用PHP生成完整字符串"""
    php_code = f'''
mt_srand({seed});
$charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
$str = "";
for ($i = 0; $i < 20; $i++) {{
    $str .= substr($charset, mt_rand(0, 61), 1);
}}
echo $str;
'''
    result = subprocess.run(["php", "-r", php_code], capture_output=True, text=True)
    return result.stdout.strip()

def submit_answer(session, answer):
    """提交答案"""
    resp = session.post("http://b644583a-05a9-4dbf-8264-e9e41c1dd2ff.node5.buuoj.cn:81/check.php", data={"num": answer})
    match = re.search(r'<p id=flag>([^<]+)</p>', resp.text)
    if match:
        return match.group(1)
    return None

# 主流程
print("1. 获取前缀和session...")
prefix, session = get_prefix_and_session()
print(f"   前缀: {prefix}")

print("2. 转换参数...")
args = prefix_to_args(prefix)
print(f"   参数: {' '.join(args[:20])}...")

print("3. 破解种子...")
seed = crack_seed(args)
print(f"   种子: {seed}")

print("4. 生成完整字符串...")
full_str = generate_full_string(seed)
print(f"   完整字符串: {full_str}")

print("5. 提交答案...")
result = submit_answer(session, full_str)
print(f"   结果: {result}")
