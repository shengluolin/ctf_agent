<?php
// 已知的前10位字符串
$known_str = "tNrC4gANXN";
$str_long1 = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

// 暴力破解种子
for ($seed = 0; $seed <= 999999999; $seed++) {
    mt_srand($seed);
    $str = '';
    $len1 = 20;

    for ($i = 0; $i < $len1; $i++) {
        $str .= substr($str_long1, mt_rand(0, strlen($str_long1) - 1), 1);
    }

    // 检查前10位是否匹配
    if (substr($str, 0, 10) === $known_str) {
        echo "Found seed: $seed\n";
        echo "Full string: $str\n";
        break;
    }

    // 进度显示
    if ($seed % 10000000 == 0) {
        echo "Progress: $seed\n";
    }
}
?>
