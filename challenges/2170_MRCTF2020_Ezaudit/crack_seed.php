<?php
// 公钥字符集
$strings1 = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
$public_key = 'KVQP0LdJKRaV3n9D';

// 将每个字符转换为 mt_rand 的输出值
for ($i = 0; $i < strlen($public_key); $i++) {
    $char = $public_key[$i];
    $pos = strpos($strings1, $char);
    echo "$pos ";
}
echo "\n";
?>
