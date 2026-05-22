<?php
// Test the serialization escape locally

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Simulate the session
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = base64_encode('guest_img.png');

echo "Original session:\n";
var_dump($_SESSION);

echo "\nSerialized:\n";
$serialized = serialize($_SESSION);
echo $serialized . "\n";

echo "\nFiltered:\n";
$filtered = filter($serialized);
echo $filtered . "\n";

echo "\nUnserialized:\n";
$unserialized = unserialize($filtered);
var_dump($unserialized);

// Now test with escape
$_SESSION['user'] = 'flag";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';

echo "\n\n=== Escape test ===\n";
echo "Session with escape:\n";
var_dump($_SESSION);

echo "\nSerialized:\n";
$serialized = serialize($_SESSION);
echo $serialized . "\n";
echo "Length: " . strlen($serialized) . "\n";

echo "\nFiltered:\n";
$filtered = filter($serialized);
echo $filtered . "\n";
echo "Length: " . strlen($filtered) . "\n";

echo "\nUnserialized:\n";
try {
    $unserialized = unserialize($filtered);
    var_dump($unserialized);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
