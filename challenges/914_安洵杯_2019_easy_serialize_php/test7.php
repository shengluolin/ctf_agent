<?php
// I see the issue now. The filter is applied to the ENTIRE serialized string,
// not just the values!
// 
// Let me trace through more carefully:
// 
// Original serialized: a:3:{s:4:"user";s:4:"flag";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After filter (removing 'flag'): a:3:{s:4:"user";s:4:"";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, that's not right. Let me check the actual filter output.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$_SESSION = [];
$_SESSION['user'] = 'flag';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n";
echo "Length: " . strlen($serialized) . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n";
echo "Length: " . strlen($filtered) . "\n\n";

// Check if 'flag' was removed
echo "Difference:\n";
echo "Original length: " . strlen($serialized) . "\n";
echo "Filtered length: " . strlen($filtered) . "\n";
echo "Removed: " . (strlen($serialized) - strlen($filtered)) . " chars\n\n";

// The key insight: the filter removes 'flag' from the VALUE, not from the serialized format
// So we have:
// s:4:"flag" -> s:4:"" (the 'flag' is removed, but the length 4 remains)
// 
// But wait, looking at the filtered output, it seems like the filter didn't remove 'flag'!

// Let me check if the filter is working correctly
$test = "flag";
echo "Filter test: '$test' -> '" . filter($test) . "'\n\n";

// Ah! The filter is case-insensitive (/i modifier), so it should remove 'flag'
// Let me check the serialized string again

// Actually, I think I see the issue. The serialized string contains:
// s:4:"flag"
// 
// The filter removes 'flag' from the entire string, so:
// s:4:"flag" -> s:4:""
// 
// But the quotes are part of the serialized format, not the content!
// So after filter, we have:
// s:4:""
// 
// The parser sees: string of length 4, content is "" (empty string)
// But "" is 2 chars (two quotes), not empty!
// 
// Wait, no. The quotes are delimiters, not content.
// s:4:"flag" means: string, length 4, content is the 4 chars between the quotes: f, l, a, g
// 
// After filter removes 'flag', we have:
// s:4:""
// The content between the quotes is now empty (0 chars)
// But the length still says 4!
// 
// So the parser tries to read 4 bytes from an empty string, which causes an error.

// Let me verify this by looking at the actual filtered string
echo "Checking filtered string:\n";
echo "Position of 's:4:\"': " . strpos($filtered, 's:4:"') . "\n";
echo "Substring around that position: '" . substr($filtered, strpos($filtered, 's:4:"'), 20) . "'\n\n";

// Hmm, the filtered string shows s:4:"user", not s:4:""
// That means the filter didn't remove 'flag' from the serialized string!

// Oh wait, I think I see the issue. The serialized string is:
// a:3:{s:4:"user";s:4:"flag";...}
// 
// The filter removes 'flag' from the ENTIRE string, including the keys and values!
// But 'user' doesn't contain 'flag', so it's not affected.
// The value 'flag' is removed, leaving:
// a:3:{s:4:"user";s:4:"";...}
// 
// Let me check if this is the case

// Find the position of the user value
$user_value_start = strpos($filtered, 's:4:"') + 5; // After s:4:"
echo "User value starts at position: $user_value_start\n";
echo "Chars at that position: '" . substr($filtered, $user_value_start, 10) . "'\n\n";

// Actually, let me just print the filtered string character by character
echo "Filtered string (with positions):\n";
for ($i = 0; $i < strlen($filtered); $i++) {
    echo "$i: '" . $filtered[$i] . "'\n";
}

