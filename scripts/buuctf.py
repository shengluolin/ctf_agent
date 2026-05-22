#!/usr/bin/env python3
"""
BUUCTF API 辅助脚本
用法:
  python3 buuctf.py start <cid>     # 启动容器，输出 URL
  python3 buuctf.py page <url>      # 获取页面内容
  python3 buuctf.py destroy <cid>   # 销毁容器
  python3 buuctf.py submit <cid> <flag>  # 提交 flag
"""
import requests, json, sys, time

COOKIE = "next=https://buuoj.cn/; user_data=gAAAAABp-rRX1ro41hMAhWd1jkGmULtAA32qZwD2Qi3uke9CZH-phFGHKjxQVbknMQe6x1mP48u77pLsOjGi4pYaNDuycsrNEraYcUDH1B6xVa_Wt8plVYx6eBLeRBd1TRHkEWXZmd4f8nqXthJvaJonnwJGmcEGm3CxmSso4BSXxADX3ac8aSQ=; session=8d80f7e2-f85d-475b-bf76-de48bb93b9ba.ZMr1sMOm-Q1cjUTVMr7976AOZNo"
CSRF = "f5e28a018c541e69c72c273af0685d589e4dc18877f18e3703b33ec5cfc61dad"
BUU = "https://buuoj.cn"
H_BUU = {"Cookie": COOKIE, "Accept": "application/json", "Content-Type": "application/json", "CSRF-Token": CSRF}

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

def start(cid):
    """启动容器，返回 URL"""
    buu(f"/plugins/ctfd-whale/challenge/{cid}/container", "POST")
    for _ in range(20):
        time.sleep(3)
        d = buu(f"/plugins/ctfd-whale/challenge/{cid}/container")
        if d.get("domain"):
            return f"http://{d['domain']}:{d['http_port']}"
    return None

def get_page(url):
    """获取页面内容，截取关键部分"""
    try:
        r = requests.get(url, timeout=15)
        text = r.text
        # 截取前 3000 字符 + 省略号
        if len(text) > 3000:
            return text[:3000] + "\n... (页面过长，已截断)"
        return text
    except Exception as e:
        return f"获取失败: {e}"

def submit(cid, flag):
    """提交 flag"""
    r = buu("/api/v1/challenges/attempt", "POST", {"challenge_id": cid, "submission": flag})
    return r

def destroy(cid):
    """销毁容器"""
    buu(f"/plugins/ctfd-whale/challenge/{cid}/container", "DELETE")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "start":
        cid = int(sys.argv[2])
        url = start(cid)
        if url:
            print(f"URL: {url}")
        else:
            print("ERROR: 容器启动失败")

    elif cmd == "page":
        url = sys.argv[2]
        print(get_page(url))

    elif cmd == "destroy":
        cid = int(sys.argv[2])
        destroy(cid)
        print("已销毁")

    elif cmd == "submit":
        cid = int(sys.argv[2])
        flag = sys.argv[3]
        result = submit(cid, flag)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        print(f"未知命令: {cmd}")
        print(__doc__)
