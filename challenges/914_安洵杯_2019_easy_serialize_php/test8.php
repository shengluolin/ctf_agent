<?php
// The key insight:
// - EXPANSION (0CTF 2016): Parser reads N bytes and stops, leaving extra bytes as next field
// - SHRINKING (our case): Parser reads N bytes and reads past the intended boundary
// 
// For SHRINKING, we need to make the parser read content that includes valid serialized data
// 
// The trick: use the shrinking to make the parser "skip" past the original structure
// and read our injected content as the NEXT element

// Let me think about this from the perspective of the parser:
// 
// After filter: a:3:{s:4:"user";s:N:"";...}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:N:" - value 1
//   Parser reads N bytes from "" (empty string)
//   Since "" is empty, parser reads from the next position
//   
//   The next position is: ";s:8:"function"...
//   Parser reads N bytes from this position
//   
//   If N = 4, parser reads: ";s: (4 bytes)
//   Then parser expects closing quote, but sees 8
//   Error!

// So for shrinking, the parser reads from the position after the empty string
// 
// The trick is to make the parser read content that forms a valid structure
// 
// If we have:
// s:4:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}
// 
// Parser reads 4 bytes from "" (empty)
// Reads: ";s: (4 bytes)
// Then expects closing quote, sees 3
// Error!

// Hmm, this doesn't work because the parser expects a closing quote after reading N bytes

// Let me think about this differently.
// 
// What if we use the shrinking to consume the ENTIRE remaining original structure?
// 
// The remaining structure: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// Length: 73 chars
// 
// If we generate 73 chars of overflow, the parser reads 73 bytes from ""
// Reads: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";} (73 bytes)
// 
// Then parser expects closing quote
// But there's no more content!
// Error!

// Wait, let me trace through more carefully.
// 
// After filter: a:3:{s:4:"user";s:73:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:73:" - value 1
//   Parser reads 73 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   
//   Parser reads: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";} (73 bytes)
//   This is the entire remaining structure!
//   
//   Then parser expects closing quote
//   But there's no more content (the string ends with })
//   Error!

// Hmm, this still doesn't work...

// Let me try a different approach:
// What if we use the shrinking to inject content BEFORE the closing quote?
// 
// The serialized format is: s:N:"CONTENT";
// 
// If CONTENT shrinks, the parser reads N bytes from the shorter CONTENT
// This means the parser reads past the closing quote!
// 
// For example:
// CONTENT = "flag" (4 chars)
// After filter: CONTENT = "" (0 chars)
// 
// Serialized: s:4:"flag";
// After filter: s:4:"";
// 
// Parser reads 4 bytes from position after opening quote
// Position after opening quote: " (closing quote)
// Parser reads: " (1), ; (2), s (3), : (4) = 4 bytes
// 
// Wait, the closing quote and semicolon are part of the serialized format!
// So the parser reads them as part of the CONTENT!
// 
// Then parser expects closing quote
// But the next char is whatever comes after the original closing quote and semicolon
// 
// In the full context:
// a:3:{s:4:"user";s:4:"";s:8:"function"...
// 
// After reading s:4:"", the parser has read:
// - Opening quote: "
// - CONTENT: ";s: (4 bytes, including closing quote and semicolon of the empty string)
// 
// Then parser expects closing quote
// Next char: 8
// Error!

// I think the issue is that the parser reads the CONTENT, then expects closing quote
// But the closing quote is already part of the CONTENT!

// Let me try to understand this by testing with a simple case

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Test: what happens when we unserialize a string with length mismatch?
$test = 's:4:"";s:8:"function"';
echo "Test string: $test\n";
$result = @unserialize($test);
echo "Result: ";
var_dump($result);
echo "\n";

// Test with a longer mismatch
$test2 = 's:10:"";s:8:"function"';
echo "Test string: $test2\n";
$result2 = @unserialize($test2);
echo "Result: ";
var_dump($result2);
echo "\n";

// Test with content that forms valid structure
$test3 = 's:4:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';
echo "Test string: $test3\n";
$result3 = @unserialize($test3);
echo "Result: ";
var_dump($result3);
echo "\n";

// Actually, let me think about this from the perspective of the serialized format
// 
// The format is: s:N:"CONTENT";
// 
// The parser:
// 1. Reads s:N:" - identifies a string of length N
// 2. Reads N bytes as CONTENT
// 3. Reads "; - closing quote and semicolon
// 
// If CONTENT is shorter than N, the parser reads past the closing quote!
// 
// For example:
// s:4:"" 
// 
// Parser reads:
// 1. s:4:" - string of length 4
// 2. Reads 4 bytes from position after opening quote
//    Position after opening quote: " (closing quote)
//    Reads: " (1), ; (2), s (3), : (4) = 4 bytes
//    CONTENT = ";s:
// 3. Reads "; - closing quote and semicolon
//    But the next char is 8, not "
//    Error!

// So the parser reads the closing quote as part of the CONTENT!
// 
// The trick is to make the CONTENT include the closing quote and semicolon,
// and then the parser continues parsing from the next position!

// Let me test this:
// s:6:"";s:3:"
// 
// Parser reads:
// 1. s:6:" - string of length 6
// 2. Reads 6 bytes from position after opening quote
//    Position after opening quote: " (closing quote)
//    Reads: " (1), ; (2), s (3), : (4), 3 (5), : (6) = 6 bytes
//    CONTENT = ";s:3:
// 3. Reads "; - closing quote and semicolon
//    Next char: "
//    Reads: " (closing quote)
//    Next char: ;
//    Reads: ; (semicolon)
//    Success!
// 
// 4. Parser continues from next position
//    Next position: img";s:20:"...
//    Parser expects a value (since we just read a key)
//    Parser reads: s:20:"..."

// Wait, this doesn't make sense. Let me trace through more carefully.

// Actually, I think I need to understand the serialized format better.
// 
// The format is: s:N:"CONTENT";
// 
// CONTENT is the string between the quotes.
// N is the length of CONTENT.
// 
// After reading N bytes of CONTENT, the parser reads the closing quote and semicolon.
// 
// If CONTENT is shorter than N, the parser reads past the closing quote!
// 
// For example:
// s:4:"" 
// 
// CONTENT should be 4 bytes, but "" has 0 bytes between the quotes.
// Parser reads 4 bytes starting from position after opening quote.
// Position after opening quote: " (closing quote)
// 
// But wait, the closing quote is at position 0 (relative to the opening quote).
// CONTENT should be between the quotes, so position 0 is the closing quote!
// 
// Hmm, this is confusing. Let me just test it.

// Test: serialize a string and check the format
$test_str = "test";
$serialized = serialize($test_str);
echo "Serialized 'test': $serialized\n\n";

// Test: what if we manually create a malformed serialized string?
$malformed = 's:4:"xy"';
echo "Malformed: $malformed\n";
$result = @unserialize($malformed);
echo "Result: ";
var_dump($result);
echo "\n";

// Test: what if CONTENT is empty but length says 4?
$malformed2 = 's:4:""';
echo "Malformed: $malformed2\n";
$result2 = @unserialize($malformed2);
echo "Result: ";
var_dump($result2);
echo "\n";

// Test: what if we have extra content after the closing quote?
$malformed3 = 's:0:"extra"';
echo "Malformed: $malformed3\n";
$result3 = @unserialize($malformed3);
echo "Result: ";
var_dump($result3);
echo "\n";

