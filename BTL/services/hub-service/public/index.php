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
    'data' => [
        'order_code' => 'ORD-HUNRE-98471',
        'role' => 'BUYER',
        'token' => '55AF10A4664F40F6',
        'expires_in_seconds' => 25,
        'qr_payload' => 'HUNRE:ORD-HUNRE-98471:1:BUYER:55AF10A4664F40F6'
    ]
]);
