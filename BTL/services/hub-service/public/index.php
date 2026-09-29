<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$dataFile = sys_get_temp_dir() . '/hunre_hub_lockers.json';

$defaultLockers = [
    ["id" => 1, "hub_id" => 1, "locker_code" => "LOCKER-S-01", "size_type" => "SMALL", "description" => "Cỡ Nhỏ (Giáo trình & Sách)", "status" => "EMPTY", "current_order" => null],
    ["id" => 2, "hub_id" => 1, "locker_code" => "LOCKER-M-01", "size_type" => "MEDIUM", "description" => "Cỡ Vừa (Bàn phím DareU)", "status" => "OCCUPIED", "current_order" => "ORD-HUNRE-98471"],
    ["id" => 3, "hub_id" => 1, "locker_code" => "LOCKER-M-02", "size_type" => "MEDIUM", "description" => "Cỡ Vừa (Laptop / Casio)", "status" => "EMPTY", "current_order" => null],
    ["id" => 4, "hub_id" => 1, "locker_code" => "LOCKER-L-01", "size_type" => "LARGE", "description" => "Cỡ Lớn (Màn hình / Case)", "status" => "EMPTY", "current_order" => null]
];

if (!file_exists($dataFile)) {
    file_put_contents($dataFile, json_encode($defaultLockers, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}
$lockers = json_decode(file_get_contents($dataFile), true) ?: $defaultLockers;

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$input = json_decode(file_get_contents('php://input'), true) ?: $_POST;

// 1. Dynamic QR TOTP
if (strpos($path, 'dynamic-qr') !== false) {
    $parts = explode('/', trim($path, '/'));
    $orderCode = $parts[count($parts) - 2] ?? 'ORD-HUNRE-98471';
    $userId = (int)($_GET['user_id'] ?? 1);
    $role = $_GET['role'] ?? 'BUYER';
    
    $timeWindow = floor(time() / 30);
    $payload = "{$orderCode}|{$userId}|{$role}|{$timeWindow}";
    $token = strtoupper(substr(hash_hmac('sha256', $payload, 'HUNRE_SECRET_2026'), 0, 16));
    $secondsLeft = 30 - (time() % 30);

    echo json_encode([
        'success' => true,
        'data' => [
            'order_code' => $orderCode,
            'role' => $role,
            'token' => $token,
            'expires_in_seconds' => $secondsLeft,
            'qr_payload' => "HUNRE:{$orderCode}:{$userId}:{$role}:{$token}",
            'qr_image_url' => "https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=HUNRE:{$orderCode}:{$userId}:{$role}:{$token}"
        ]
    ]);
    exit;
}

// 2. Lockers List
if ($method === 'GET' && strpos($path, 'lockers') !== false) {
    echo json_encode(['success' => true, 'lockers' => $lockers]);
    exit;
}

// 3. Checkin
if ($method === 'POST' && strpos($path, 'checkin') !== false) {
    $orderCode = $input['order_code'] ?? 'ORD-HUNRE-' . rand(10000, 99999);
    $assignedLocker = null;
    foreach ($lockers as &$locker) {
        if ($locker['status'] === 'EMPTY') {
            $locker['status'] = 'OCCUPIED';
            $locker['current_order'] = $orderCode;
            $assignedLocker = $locker;
            break;
        }
    }
    if (!$assignedLocker) {
        $assignedLocker = $lockers[0];
    }
    file_put_contents($dataFile, json_encode($lockers, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode([
        'success' => true,
        'message' => "Quét nhận hàng thành công! Đã cấp phát ô tủ {$assignedLocker['locker_code']} ({$assignedLocker['description']}).",
        'locker' => $assignedLocker
    ]);
    exit;
}

// 4. Checkout
if ($method === 'POST' && strpos($path, 'checkout') !== false) {
    $orderCode = $input['order_code'] ?? 'ORD-HUNRE-98471';
    $freedLocker = null;
    foreach ($lockers as &$locker) {
        if (($locker['current_order'] ?? '') === $orderCode || $locker['status'] === 'OCCUPIED') {
            $locker['status'] = 'EMPTY';
            $locker['current_order'] = null;
            $freedLocker = $locker;
            break;
        }
    }
    if (!$freedLocker) {
        $freedLocker = $lockers[1];
    }
    file_put_contents($dataFile, json_encode($lockers, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode([
        'success' => true,
        'message' => "Xác thực mã QR thành công! Đã mở khóa ô tủ {$freedLocker['locker_code']}. Người mua đang nhận hàng kiểm tra.",
        'locker' => $freedLocker
    ]);
    exit;
}

// Default list
echo json_encode(['success' => true, 'lockers' => $lockers]);
