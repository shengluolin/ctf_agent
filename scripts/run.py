#!/usr/bin/env python3
"""
BUUCTF CTF Agent - Claude Code 驱动的自动解题
用法:
  python3 run.py              # 跑全部10道题
  python3 run.py 703          # 只跑一道
  python3 run.py --skip-solved  # 跳过已有WP的题
"""
import subprocess, json, time, re, sys, os, requests
from pathlib import Path

# ── 路径 ──
BASE = Path("/home/lls/data/ctf-agent")
CHALLENGES = BASE / "challenges"
WPS = BASE / "wps"
LOGS = BASE / "logs"

# ── BUUCTF API ──
COOKIE = "next=https://buuoj.cn/; user_data=gAAAAABp-rRX1ro41hMAhWd1jkGmULtAA32qZwD2Qi3uke9CZH-phFGHKjxQVbknMQe6x1mP48u77pLsOjGi4pYaNDuycsrNEraYcUDH1B6xVa_Wt8plVYx6eBLeRBd1TRHkEWXZmd4f8nqXthJvaJonnwJGmcEGm3CxmSso4BSXxADX3ac8aSQ=; session=8d80f7e2-f85d-475b-bf76-de48bb93b9ba.ZMr1sMOm-Q1cjUTVMr7976AOZNo"
CSRF = "f5e28a018c541e69c72c273af0685d589e4dc18877f18e3703b33ec5cfc61dad"
BUU = "https://buuoj.cn"
H_BUU = {"Cookie": COOKIE, "Accept": "application/json", "Content-Type": "application/json", "CSRF-Token": CSRF}

# ── 题目列表 ──
from challenge_list import CHALLENGE_LIST


def buu(path, method="GET", data=None):
    try:
        if method == "POST":
            r = requests.post(f"{BUU}{path}", headers=H_BUU, json=data or {}, timeout=15)
        elif method == "DELETE":
            r = requests.delete(f"{BUU}{path}", headers=H_BUU, timeout=15)
        else:
            r = requests.get(f"{BUU}{path}", headers=H_BUU, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def start_container(cid):
    """启动容器，返回 URL"""
    buu(f"/plugins/ctfd-whale/challenge/{cid}/container", "POST")
    for _ in range(20):
        time.sleep(3)
        d = buu(f"/plugins/ctfd-whale/challenge/{cid}/container")
        # 格式1: {"domain": "xxx.node5.buuoj.cn", "http_port": 81}
        if d.get("domain"):
            return f"http://{d['domain']}:{d['http_port']}"
        # 格式2: {"lan_domain": "xxx", "ip": "node5.buuoj.cn", "port": 26536}
        if d.get("lan_domain") and d.get("port"):
            return f"http://{d['lan_domain']}.{d['ip']}:{d['port']}"
    return None


def destroy_container(cid):
    buu(f"/plugins/ctfd-whale/challenge/{cid}/container", "DELETE")


def run_claude(cid, name, url, challenge_dir, wp_path):
    """调用 Claude Code 解题"""
    # 读取模板
    template = (BASE / "scripts" / "prompt_template.md").read_text()
    prompt = template.format(
        name=name, url=url, cid=cid,
        challenge_dir=challenge_dir, wp_path=wp_path,
        cookie=COOKIE, csrf=CSRF,
    )

    log_path = LOGS / f"{cid}_{name.split(']')[0].replace('[','')}.log"

    try:
        result = subprocess.run(
            ["claude", "--print", "--allowedTools", "Bash"],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=3600,
            start_new_session=True,  # 进程组管理，超时时能杀掉子进程
        )
        stdout = result.stdout
        stderr = result.stderr
        log_path.write_text(f"=== STDOUT ===\n{stdout}\n=== STDERR ===\n{stderr}")

        # 从 stdout 提取 WP（找 --- 开头的 YAML frontmatter）
        if "---" in stdout:
            # 找到第一个 --- 的位置
            start = stdout.index("---")
            wp_content = stdout[start:]
            wp_path.write_text(wp_content)
            return True

        return False
    except subprocess.TimeoutExpired:
        log_path.write_text("TIMEOUT after 3600s")
        return False
    except Exception as e:
        log_path.write_text(f"ERROR: {e}")
        return False


def main():
    skip_solved = "--skip-solved" in sys.argv
    only_cid = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            only_cid = int(arg)

    print(f"=== BUUCTF CTF Agent (Claude Code) ===", flush=True)
    print(f"题目数: {len(CHALLENGE_LIST)}", flush=True)

    for cid, name in CHALLENGE_LIST:
        if only_cid and cid != only_cid:
            continue

        short_name = re.sub(r'[^\w]', '_', name).strip('_')
        challenge_dir = CHALLENGES / f"{cid}_{short_name}"
        wp_path = WPS / f"{cid}_{short_name}.md"

        print(f"\n{'='*50}", flush=True)
        print(f"[{cid}] {name}", flush=True)

        # 跳过已有WP
        if skip_solved and wp_path.exists():
            print(f"  ⏭ 已有WP，跳过", flush=True)
            continue

        # 创建题目目录
        challenge_dir.mkdir(parents=True, exist_ok=True)

        # 启动容器（带重试）
        print(f"  🔄 启动容器...", flush=True)
        url = start_container(cid)
        if not url:
            print(f"  ⚠ 第一次失败，等60秒重试...", flush=True)
            time.sleep(60)
            url = start_container(cid)
        if not url:
            print(f"  ✗ 容器启动失败", flush=True)
            time.sleep(30)
            continue
        print(f"  ✓ URL: {url}", flush=True)

        # 调 Claude Code 解题
        print(f"  🤖 Claude Code 解题中...", flush=True)
        success = run_claude(cid, name, url, challenge_dir, wp_path)

        if success:
            print(f"  ✓ WP 已保存: {wp_path}", flush=True)
        else:
            print(f"  ✗ 解题失败，查看日志: {LOGS}/", flush=True)

        # 销毁容器
        destroy_container(cid)
        print(f"  🗑 容器已销毁", flush=True)

        # 间隔（避免频率限制）
        time.sleep(30)

    # 汇总
    wps = list(WPS.glob("*.md"))
    print(f"\n{'='*50}")
    print(f"完成! WP: {len(wps)}/{len(CHALLENGE_LIST)}")
    for wp in sorted(wps):
        print(f"  📄 {wp.name}")


if __name__ == "__main__":
    main()
