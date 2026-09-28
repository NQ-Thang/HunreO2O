<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);

if (str_contains($uri, '/trust-score')) {
    echo json_encode([
        'success' => true,
        'data' => [
            'user_id' => 1,
            'full_name' => 'Nguyễn Văn An',
            'student_code' => '20211001',
            'trust_score' => 520,
            'tier' => 'BẠC (Sinh viên uy tín tiêu chuẩn)',
            'benefits' => ['can_barter' => true, 'deposit_discount' => '0%']
        ]
    ]);
    exit;
}

echo json_encode([
    'service' => 'HUNRE Auth & Trust Score Service',
    'status' => 'RUNNING',
    'endpoints' => ['/api/v1/auth/register', '/api/v1/auth/login', '/api/v1/auth/trust-score/{id}']
]);
