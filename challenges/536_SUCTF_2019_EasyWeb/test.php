<?php
$forbidden = "/[\x00- 0-9A-Za-z\'\"\`~_&.,|=[\x7F]+/i";
echo "Allowed characters:\n";
for($i = 33; $i < 127; $i++) {
    $c = chr($i);
    if(!preg_match($forbidden, $c)) {
        echo "$i:" . $c . " ";
    }
}
echo "\n";

echo "\nFinding XOR pairs:\n";
$targets = ['_' => 95, 'G' => 71, 'E' => 69, 'T' => 84];

foreach($targets as $name => $target) {
    echo "$name ($target): ";
    for($i = 33; $i < 127; $i++) {
        $c1 = chr($i);
        if(preg_match($forbidden, $c1)) continue;
        for($j = 33; $j < 127; $j++) {
            $c2 = chr($j);
            if(preg_match($forbidden, $c2)) continue;
            if(($i ^ $j) == $target) {
                echo "($c1^$c2) ";
                break 2;
            }
        }
    }
    echo "\n";
}
?>
