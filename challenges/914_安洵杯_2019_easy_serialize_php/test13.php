<?php
// I think I finally understand the escape trick!
// 
// The key insight: when the filter SHRINKS the string, the serialized length is LARGER than actual.
// PHP reads N bytes from the CONTENT, but the CONTENT is shorter than N.
// So PHP reads past the closing quote and semicolon!
// 
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// If we can make the Nth byte be followed by ";, PHP will continue parsing!
// 
// The trick is to make PHP read content that includes the closing quote and semicolon
// of the current element, and then the next chars are our injected element!

// Let me trace through with a specific example:
// 
// Original serialized: a:3:{s:4:"user";s:45:"flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After filter: a:3:{s:4:"user";s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:45:" - value is string of length 45
//   PHP reads 45 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   PHP reads: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"f (45 bytes)
//   CONTENT = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"f
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: u (from "unction")
//   Expected ", got u
//   Error!

// So the issue is that the CONTENT ends with "f" and the next char is "u", not "!

// The trick is to adjust the length so that the CONTENT ends right before a ";!
// 
// Let me think about this:
// 
// We want the CONTENT to end right before a "; in the remaining string.
// 
// The remaining string after the empty string is:
// ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// We want to find a position where "; appears.
// 
// Position 0: "
// Position 1: ;
// Position 2: s
// ...
// Position 40: }
// Position 41: "
// Position 42: ;
// Position 43: s
// ...
// 
// So "; appears at positions 0-1 and 41-42.
// 
// If we make the CONTENT end at position 40 (right before the "; at 41-42),
// then PHP will see "; and continue parsing!

// Let me calculate:
// CONTENT length = 41 (positions 0-40)
// 
// The CONTENT is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Let me count: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
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

// So if we have:
// s:41:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";...
// 
// PHP reads 41 bytes from "":
// CONTENT = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: " (from the original structure)
// PHP reads: " (closing quote)
// Next char: ; (from the original structure)
// PHP reads: ; (semicolon)
// 
// PHP found "; and continues parsing!
// 
// The next chars are: s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// PHP parses this as the remaining elements of the array!

// But wait, the array count is 3, and we already have:
// - user (key)
// - CONTENT (value)
// 
// So we need 2 more elements: function and img.
// 
// The remaining chars are: s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// s:8:"function" - key 2
// s:10:"show_image" - value 2
// s:3:"img" - key 3
// s:20:"Z3Vlc3RfaW1nLnBuZw==" - value 3
// } - end of array
// 
// So the final array is:
// user = ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// function = show_image
// img = Z3Vlc3RfaW1nLnBuZw==

// This is not what we want! We want img = ZDBnM19mMWFnLnBocA==!

// The issue is that our injected content is being read as the VALUE of user,
// not as separate elements!

// Let me think about this differently.
// 
// The key insight from the 0CTF 2016 writeup:
// The filter EXPANDS the string (where->hacker), creating EXTRA bytes.
// The serialized length says N bytes, but the actual string is N+1 bytes per "where".
// PHP reads N bytes and STOPS, leaving the EXTRA bytes as the next serialized element!
// 
// In our case, the filter SHRINKS the string (flag->''), creating FEWER bytes.
// The serialized length says N bytes, but the actual string is N-4 bytes per "flag".
// PHP reads N bytes and reads PAST the intended boundary!

// These are opposite effects!
// 
// For EXPANSION: PHP reads N bytes and stops, leaving extra bytes.
// For SHRINKING: PHP reads N bytes and reads past the boundary.

// So the escape trick for SHRINKING is different from EXPANSION!

// Let me think about how to exploit SHRINKING:
// 
// When PHP reads past the boundary, it reads content from the next element.
// We want this content to form a valid serialized structure.
// 
// But the content is read as the VALUE of the current element, not as a new element!

// Hmm, this is tricky. Let me re-read the 0CTF 2016 writeup...

// Actually, I think I've been misunderstanding the escape trick.
// 
// Let me re-read the writeup:
// "The serialized length field says N bytes, but after expansion the actual string is longer,
// causing the PHP deserializer to read past the intended boundary and parse attacker-controlled
// data as serialized fields."
// 
// So the key is: PHP reads past the boundary and PARSES the extra data as serialized fields!
// 
// But in my tests, PHP reads the extra data as the VALUE of the current element,
// not as separate fields!

// Let me test this more carefully.

// Test: what happens when we have extra content after a serialized string?
$test = 's:4:"test";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
echo "Test: $test\n";
$result = @unserialize($test);
var_dump($result);
echo "\n";

// Test: what happens with an array?
$test2 = 'a:3:{s:4:"user";s:4:"test";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";}';
echo "Test 2: $test2\n";
$result2 = @unserialize($test2);
var_dump($result2);
echo "\n";

