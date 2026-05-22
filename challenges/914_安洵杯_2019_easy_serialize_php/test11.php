<?php
// Let me understand PHP's unserialize behavior better
// 
// The serialized format is: s:N:"CONTENT";
// 
// CONTENT is the string between the quotes.
// N is the length of CONTENT in bytes.
// 
// For example:
// s:4:"test" - CONTENT is "test" (4 bytes)
// s:0:"" - CONTENT is "" (0 bytes)

// Let me test what happens with different inputs

// Valid string
$test1 = 's:4:"test";';
echo "Test 1: $test1\n";
$result1 = unserialize($test1);
var_dump($result1);
echo "\n";

// String with length mismatch (too short)
$test2 = 's:4:"te";';
echo "Test 2: $test2\n";
$result2 = @unserialize($test2);
var_dump($result2);
echo "\n";

// String with length mismatch (too long)
$test3 = 's:4:"testing";';
echo "Test 3: $test3\n";
$result3 = @unserialize($test3);
var_dump($result3);
echo "\n";

// String with special chars
$test4 = 's:4:"te;t";';
echo "Test 4: $test4\n";
$result4 = @unserialize($test4);
var_dump($result4);
echo "\n";

// String with quote in content
$test5 = 's:5:"te\"t";';
echo "Test 5: $test5\n";
$result5 = @unserialize($test5);
var_dump($result5);
echo "\n";

// Actually, in PHP serialize, quotes are not escaped!
// Let me test
$test_str = 'te"t';
$serialized = serialize($test_str);
echo "Serialized 'te\"t': $serialized\n";
$result5b = unserialize($serialized);
var_dump($result5b);
echo "\n";

// String with closing brace in content
$test6 = 's:4:"te}t";';
echo "Test 6: $test6\n";
$result6 = @unserialize($test6);
var_dump($result6);
echo "\n";

// Now let me understand what happens with the escape
// 
// When the filter removes 'flag' from the serialized string:
// s:4:"flag" -> s:4:""
// 
// The serialized format is now: s:4:""
// This means: string of length 4, content is "" (empty)
// 
// But "" is only 0 bytes, not 4!
// 
// PHP's unserialize will try to read 4 bytes from position after opening quote.
// Position after opening quote: " (closing quote)
// 
// PHP reads: " (1 byte), then continues reading until it has 4 bytes.
// 
// Let me trace through:
// s:4:""
// Position 0: s
// Position 1: :
// Position 2: 4
// Position 3: :
// Position 4: " (opening quote)
// Position 5: " (closing quote)
// Position 6: ;
// 
// PHP reads 4 bytes starting from position 5 (after opening quote at position 4).
// Position 5: " (closing quote)
// Position 6: ;
// Position 7: ? (end of string)
// 
// PHP only has 2 bytes to read (positions 5 and 6), but needs 4 bytes.
// PHP reads past the end of the string, causing an error!

// Let me verify this
$test7 = 's:4:"";';
echo "Test 7: $test7\n";
$result7 = @unserialize($test7);
var_dump($result7);
echo "\n";

// What if we have more content after?
$test8 = 's:4:"";s:8:"function"';
echo "Test 8: $test8\n";
$result8 = @unserialize($test8);
var_dump($result8);
echo "\n";

// Let me trace through test8:
// s:4:"";s:8:"function"
// Position 0: s
// Position 1: :
// Position 2: 4
// Position 3: :
// Position 4: " (opening quote)
// Position 5: " (closing quote)
// Position 6: ;
// Position 7: s
// Position 8: :
// Position 9: 8
// Position 10: :
// Position 11: " (opening quote)
// Position 12: f
// ...
// Position 19: " (closing quote)
// Position 20: ;
// 
// PHP reads 4 bytes starting from position 5:
// Position 5: "
// Position 6: ;
// Position 7: s
// Position 8: :
// 
// CONTENT = ";s: (4 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Position 9: 8
// Expected ", got 8
// Error!

// So the key insight is:
// PHP reads N bytes as CONTENT, then expects "; (closing quote and semicolon).
// 
// If we can make the content after N bytes be ";, PHP will continue parsing!
// 
// For example:
// s:4:"xy";s:8:"function"
// 
// PHP reads 4 bytes: x, y, ", ;
// CONTENT = "xy";" (wait, that's only 3 bytes: x, y, ")
// 
// Hmm, I'm still confused. Let me just test.

$test9 = 's:4:"xy";s:8:"function"';
echo "Test 9: $test9\n";
$result9 = @unserialize($test9);
var_dump($result9);
echo "\n";

// What about:
$test10 = 's:3:"xy";s:8:"function"';
echo "Test 10: $test10\n";
$result10 = @unserialize($test10);
var_dump($result10);
echo "\n";

// And:
$test11 = 's:2:"xy";s:8:"function"';
echo "Test 11: $test11\n";
$result11 = @unserialize($test11);
var_dump($result11);
echo "\n";

// Let me also test with an array
$test12 = 'a:1:{s:4:"test";}';
echo "Test 12: $test12\n";
$result12 = @unserialize($test12);
var_dump($result12);
echo "\n";

// Array with length mismatch in value
$test13 = 'a:1:{s:4:"test";s:4:"";}';
echo "Test 13: $test13\n";
$result13 = @unserialize($test13);
var_dump($result13);
echo "\n";

// Array with length mismatch that reads into next element
$test14 = 'a:2:{s:4:"test";s:4:"";s:5:"extra";}';
echo "Test 14: $test14\n";
$result14 = @unserialize($test14);
var_dump($result14);
echo "\n";

