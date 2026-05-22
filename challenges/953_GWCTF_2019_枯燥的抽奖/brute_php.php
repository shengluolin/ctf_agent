<?php
$known = "wAdZ8iEIP0";
$charset = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

for ($seed = 0; $seed <= 999999999; $seed++) {
    mt_srand($seed);
    $str = '';
    for ($i = 0; $i < 10; $i++) {
        $str .= substr($charset, mt_rand(0, 61), 1);
    }
    if ($str === $known) {
        echo "Found seed: $seed\n";
        // 生成完整20位
        mt_srand($seed);
        $full = '';
        for ($i = 0; $i < 20; $i++) {
            $full .= substr($charset, mt_rand(0, 61), 1);
        }
        echo "Full string: $full\n";
        break;
    }
    if ($seed % 10000000 == 0) {
        echo "Progress: $seed\n";
    }
}
?>
