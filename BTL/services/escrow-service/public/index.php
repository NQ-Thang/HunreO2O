<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

echo json_encode([
    'success' => true,
    'order' => [
        'order_code' => 'ORD-HUNRE-98471',
        'buyer_name' => 'Nguyễn Văn An',
        'seller_name' => 'Lê Hoàng Cường',
        'product_title' => 'Bàn phím cơ DareU EK87 Blue Switch',
        'hub_name' => 'Trạm Hub CS1 (Nhà A - Phòng Đoàn Trường)',
        'locker_code' => 'LOCKER-M-01',
        'escrow_amount' => 250000.0,
        'status' => 'STORED_AT_HUB'
    ]
]);
