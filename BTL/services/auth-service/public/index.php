<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$users = [
    ["id" => 1, "student_code" => "20211001", "full_name" => "Nguyễn Văn An", "email" => "an.nv@hunre.edu.vn", "trust_score" => 520, "campus" => "CS1_HA_NOI", "wallet_balance" => 500000.0, "role" => "STUDENT", "faculty" => "Công nghệ Thông tin"],
    ["id" => 2, "student_code" => "20211002", "full_name" => "Trần Thị Bích", "email" => "bich.tt@hunre.edu.vn", "trust_score" => 480, "campus" => "CS1_HA_NOI", "wallet_balance" => 250000.0, "role" => "STUDENT", "faculty" => "Môi trường"],
    ["id" => 3, "student_code" => "20211003", "full_name" => "Lê Hoàng Cường", "email" => "cuong.lh@hunre.edu.vn", "trust_score" => 390, "campus" => "CS1_HA_NOI", "wallet_balance" => 120000.0, "role" => "STUDENT", "faculty" => "Khí tượng Thủy văn"],
    ["id" => 4, "student_code" => "HUB001", "full_name" => "Cộng Tác Viên Trạm Hub", "email" => "hub.cs1@hunre.edu.vn", "trust_score" => 999, "campus" => "CS1_HA_NOI", "wallet_balance" => 0.0, "role" => "HUB_STAFF", "faculty" => "Đoàn Thanh Niên"]
];

$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$userId = (int)($_GET['user_id'] ?? 1);

if (str_contains($uri, '/trust-score')) {
    $found = null;
    foreach ($users as $u) {
        if ($u['id'] === $userId) {
            $found = $u;
            break;
        }
    }
    if (!$found) $found = $users[0];

    $score = $found['trust_score'];
    $tier = $score >= 800 ? "KIM CƯƠNG" : ($score >= 600 ? "VÀNG" : ($score >= 400 ? "BẠC" : "ĐỒNG"));

    echo json_encode([
        'success' => true,
        'data' => [
            'user_id' => $found['id'],
            'full_name' => $found['full_name'],
            'student_code' => $found['student_code'],
            'trust_score' => $score,
            'tier' => "{$tier} (Sinh viên uy tín tiêu chuẩn)",
            'wallet_balance' => $found['wallet_balance'],
            'benefits' => ['can_barter' => true, 'deposit_discount' => $score >= 600 ? '50%' : '0%']
        ]
    ]);
    exit;
}

if (str_contains($uri, '/users')) {
    echo json_encode(['success' => true, 'users' => $users]);
    exit;
}

echo json_encode([
    'service' => 'HUNRE Auth & Trust Score Service',
    'status' => 'RUNNING',
    'users_count' => count($users),
    'endpoints' => ['/api/v1/auth/register', '/api/v1/auth/login', '/api/v1/auth/trust-score', '/api/v1/auth/users']
]);
