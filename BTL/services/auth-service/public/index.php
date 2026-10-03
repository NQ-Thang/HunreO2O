<?php
/**
 * HUNRE AUTH SERVICE - Optimized Entry Point & Router
 * Port: 8001 | PHP Standalone / Microservice Container
 * 
 * Implements Identity, Student KYC & Trust Score Engine for HUNRE O2O Platform.
 * All API contracts and JSON keys remain 100% backward-compatible.
 */

declare(strict_types=1);

// ── 1. CORS Headers & Preflight Handling ─────────────────────────────────────
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, X-Idempotency-Key');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// ── 2. Core Config & DB Initialization ───────────────────────────────────────
require_once __DIR__ . '/../app/config.php';

// ── 3. Parse Request Method, Path & Payload ──────────────────────────────────
$method = $_SERVER['REQUEST_METHOD'];
$uri    = parse_url($_SERVER['REQUEST_URI'] ?? '/', PHP_URL_PATH) ?? '/';
$uri    = rtrim($uri, '/');
if ($uri === '') {
    $uri = '/';
}

$body = [];
$rawInput = file_get_contents('php://input');
if ($rawInput !== false && $rawInput !== '') {
    $decoded = json_decode($rawInput, true);
    if (json_last_error() === JSON_ERROR_NONE && is_array($decoded)) {
        $body = $decoded;
    }
}

// ── 4. Route Dispatcher ──────────────────────────────────────────────────────

// [A] Health Check
if ($uri === '/health' || $uri === '/' || $uri === '/api/v1/auth') {
    jsonResponse([
        'service'   => 'HUNRE Auth & Trust Score Service',
        'version'   => '3.2.0',
        'status'    => 'UP',
        'timestamp' => date('Y-m-d H:i:s'),
        'endpoints' => [
            'POST /api/v1/auth/register',
            'POST /api/v1/auth/login',
            'POST /api/v1/auth/logout              [Bearer]',
            'GET  /api/v1/auth/me                  [Bearer]',
            'GET  /api/v1/auth/users               [Public/Admin]',
            'GET  /api/v1/auth/trust-score/{id}    [Public/Bearer]',
            'GET  /api/v1/auth/users/trust-score   [Query: user_id]',
            'POST /api/v1/auth/trust-score/update  [Bearer]'
        ]
    ]);
}

// [B] GET /api/v1/auth/users (Lấy danh sách người dùng)
if ($uri === '/api/v1/auth/users' && $method === 'GET') {
    $db = getDB();
    $stmt = $db->query("
        SELECT id, student_code, full_name, email, phone, faculty, campus, 
               trust_score, kyc_status, role, wallet_balance, created_at 
        FROM users 
        ORDER BY id ASC
    ");
    $users = $stmt->fetchAll();

    jsonResponse([
        'success' => true,
        'count'   => count($users),
        'users'   => $users
    ]);
}

// [C] POST /api/v1/auth/register (Đăng ký tài khoản KYC Sinh viên)
if ($uri === '/api/v1/auth/register' && $method === 'POST') {
    $studentCode = trim((string) ($body['student_code'] ?? ''));
    $fullName    = trim((string) ($body['full_name'] ?? ''));
    $email       = strtolower(trim((string) ($body['email'] ?? '')));
    $password    = (string) ($body['password'] ?? '');
    $faculty     = trim((string) ($body['faculty'] ?? 'Công nghệ Thông tin'));
    $campus      = (string) ($body['campus'] ?? 'CS1_HA_NOI');

    // Kiểm tra tính đầy đủ
    if ($studentCode === '' || $fullName === '' || $email === '' || $password === '') {
        jsonResponse([
            'success' => false, 
            'message' => 'Thiếu các trường bắt buộc: student_code, full_name, email, password.'
        ], 422);
    }

    if (strlen($password) < 6) {
        jsonResponse([
            'success' => false, 
            'message' => 'Mật khẩu phải có ít nhất 6 ký tự.'
        ], 422);
    }

    // Bắt buộc email thuộc domain HUNRE (@hunre.edu.vn)
    if (!str_ends_with($email, '@hunre.edu.vn')) {
        jsonResponse([
            'success' => false, 
            'message' => 'Lỗi KYC: Chỉ chấp nhận email định danh sinh viên Đại học Tài nguyên và Môi trường Hà Nội (@hunre.edu.vn)!'
        ], 422);
    }

    $validCampuses = ['CS1_HA_NOI', 'CS2_THANH_HOA'];
    if (!in_array($campus, $validCampuses, true)) {
        $campus = 'CS1_HA_NOI';
    }

    $db = getDB();

    // Kiểm tra trùng mã sinh viên hoặc email
    $dup = $db->prepare("SELECT id FROM users WHERE email = ? OR student_code = ? LIMIT 1");
    $dup->execute([$email, $studentCode]);
    if ($dup->fetch()) {
        jsonResponse([
            'success' => false, 
            'message' => 'Email hoặc mã sinh viên này đã được đăng ký trong hệ thống!'
        ], 409);
    }

    $passwordHash = password_hash($password, PASSWORD_BCRYPT, ['cost' => 10]);
    $stmt = $db->prepare("
        INSERT INTO users (student_code, full_name, email, password_hash, faculty, campus, trust_score, kyc_status, role, wallet_balance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 500, 'VERIFIED', 'STUDENT', 0.00, NOW(), NOW())
    ");
    $stmt->execute([$studentCode, $fullName, $email, $passwordHash, $faculty, $campus]);
    $userId = (int) $db->lastInsertId();

    jsonResponse([
        'success' => true,
        'message' => 'Đăng ký tài khoản sinh viên HUNRE thành công!',
        'data'    => [
            'user_id'      => $userId,
            'student_code' => $studentCode,
            'full_name'    => $fullName,
            'email'        => $email,
            'trust_score'  => 500,
            'tier'         => 'BẠC (Sinh viên uy tín tiêu chuẩn)',
            'campus'       => $campus,
            'faculty'      => $faculty
        ]
    ], 201);
}

// [D] POST /api/v1/auth/login (Đăng nhập & Cấp Bearer Token)
if ($uri === '/api/v1/auth/login' && $method === 'POST') {
    $email    = strtolower(trim((string) ($body['email'] ?? '')));
    $password = (string) ($body['password'] ?? '');

    if ($email === '' || $password === '') {
        jsonResponse([
            'success' => false, 
            'message' => 'Vui lòng nhập đầy đủ email và mật khẩu.'
        ], 422);
    }

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE email = ? LIMIT 1");
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user->password_hash)) {
        jsonResponse([
            'success' => false, 
            'message' => 'Email hoặc mật khẩu không chính xác.'
        ], 401);
    }

    // Sinh Bearer Token ngẫu nhiên (64 ký tự hex an toàn)
    $rawToken  = bin2hex(random_bytes(32));
    $tokenHash = hash('sha256', $rawToken);
    $prefix    = substr($rawToken, 0, 12);
    $expiresAt = date('Y-m-d H:i:s', time() + 86400); // 24 giờ

    // Dọn dẹp token cũ của user để đảm bảo 1 phiên hoạt động duy nhất
    $db->prepare("DELETE FROM api_tokens WHERE user_id = ?")->execute([$user->id]);

    // Lưu token mới
    $db->prepare("
        INSERT INTO api_tokens (user_id, token_hash, token_prefix, expires_at, created_at)
        VALUES (?, ?, ?, ?, NOW())
    ")->execute([$user->id, $tokenHash, $prefix, $expiresAt]);

    $score = (int) $user->trust_score;
    $tier  = evaluateTier($score);

    jsonResponse([
        'success'    => true,
        'message'    => 'Đăng nhập thành công!',
        'token'      => $rawToken,
        'token_type' => 'Bearer',
        'expires_at' => $expiresAt,
        'user'       => [
            'id'             => (int) $user->id,
            'student_code'   => $user->student_code,
            'full_name'      => $user->full_name,
            'email'          => $user->email,
            'trust_score'    => $score,
            'tier'           => $tier,
            'campus'         => $user->campus,
            'role'           => $user->role,
            'wallet_balance' => (float) $user->wallet_balance
        ]
    ]);
}

// [E] POST /api/v1/auth/logout (Đăng xuất & Hủy Token)
if ($uri === '/api/v1/auth/logout' && $method === 'POST') {
    $authUser  = requireAuth();
    $rawToken  = getBearerToken() ?? '';
    $tokenHash = hash('sha256', $rawToken);
    
    $db = getDB();
    $db->prepare("DELETE FROM api_tokens WHERE token_hash = ?")->execute([$tokenHash]);

    jsonResponse([
        'success' => true, 
        'message' => 'Đăng xuất thành công. Token đã bị thu hồi an toàn.'
    ]);
}

// [F] GET /api/v1/auth/me (Lấy thông tin cá nhân hiện tại từ Bearer Token)
if ($uri === '/api/v1/auth/me' && $method === 'GET') {
    $authUser = requireAuth();
    $score    = (int) $authUser->trust_score;
    $tier     = evaluateTier($score);

    jsonResponse([
        'success' => true,
        'user'    => [
            'id'                    => (int) $authUser->id,
            'student_code'          => $authUser->student_code,
            'full_name'             => $authUser->full_name,
            'email'                 => $authUser->email,
            'phone'                 => $authUser->phone ?? null,
            'campus'                => $authUser->campus,
            'faculty'               => $authUser->faculty,
            'role'                  => $authUser->role,
            'trust_score'           => $score,
            'trust_tier'            => $tier,
            'kyc_status'            => $authUser->kyc_status ?? 'VERIFIED',
            'wallet_balance'        => (float) ($authUser->wallet_balance ?? 0.0),
            'escrow_locked_balance' => (float) ($authUser->escrow_locked_balance ?? 0.0)
        ]
    ]);
}

// [G] GET /api/v1/auth/trust-score/{userId} hoặc /api/v1/auth/users/trust-score
$isTrustScorePath = preg_match('#^/api/v1/auth/trust-score/(\d+)$#', $uri, $m);
$isTrustScoreQuery = ($uri === '/api/v1/auth/users/trust-score' || $uri === '/api/v1/auth/trust-score');

if (($isTrustScorePath || $isTrustScoreQuery) && $method === 'GET') {
    $userId = $isTrustScorePath ? (int) $m[1] : (int) ($_GET['user_id'] ?? 1);

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ? LIMIT 1");
    $stmt->execute([$userId]);
    $user = $stmt->fetch();

    if (!$user) {
        jsonResponse([
            'success' => false, 
            'message' => "Không tìm thấy sinh viên với ID: {$userId}."
        ], 404);
    }

    $score = (int) $user->trust_score;
    $tier  = evaluateTier($score);

    jsonResponse([
        'success' => true,
        'data'    => [
            'user_id'      => (int) $user->id,
            'full_name'    => $user->full_name,
            'student_code' => $user->student_code,
            'trust_score'  => $score,
            'tier'         => $tier,
            'wallet_balance' => (float) ($user->wallet_balance ?? 0.0),
            'campus'       => $user->campus ?? 'CS1_HA_NOI',
            'benefits'     => [
                'can_barter'        => $score >= 200,
                'deposit_discount'  => $score >= 800 ? '100%' : ($score >= 600 ? '50%' : '0%'),
                'priority_matching' => $score >= 600
            ]
        ]
    ]);
}

// [H] POST /api/v1/auth/trust-score/update (Cập nhật điểm uy tín)
if ($uri === '/api/v1/auth/trust-score/update' && $method === 'POST') {
    $userId      = (int) ($body['user_id'] ?? 0);
    $scoreChange = (int) ($body['score_change'] ?? 0);
    $reason      = trim((string) ($body['reason'] ?? ''));

    if ($userId <= 0 || $scoreChange === 0 || $reason === '') {
        jsonResponse([
            'success' => false, 
            'message' => 'Thiếu các trường bắt buộc: user_id, score_change, reason.'
        ], 422);
    }

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ? LIMIT 1");
    $stmt->execute([$userId]);
    $user = $stmt->fetch();

    if (!$user) {
        jsonResponse([
            'success' => false, 
            'message' => 'Không tìm thấy sinh viên để cập nhật điểm.'
        ], 404);
    }

    $oldScore = (int) $user->trust_score;
    $newScore = max(0, min(1000, $oldScore + $scoreChange));

    $db->prepare("UPDATE users SET trust_score = ?, updated_at = NOW() WHERE id = ?")
       ->execute([$newScore, $userId]);

    jsonResponse([
        'success' => true,
        'message' => 'Cập nhật điểm uy tín sinh viên thành công!',
        'data'    => [
            'user_id'      => $userId,
            'old_score'    => $oldScore,
            'score_change' => $scoreChange,
            'new_score'    => $newScore,
            'tier'         => evaluateTier($newScore),
            'reason'       => $reason
        ]
    ]);
}

// ── 5. Fallback 404 Handler ──────────────────────────────────────────────────
jsonResponse([
    'success' => false,
    'message' => "Endpoint không tồn tại: [{$method}] {$uri}",
    'available_routes' => [
        'POST /api/v1/auth/register',
        'POST /api/v1/auth/login',
        'POST /api/v1/auth/logout              [Bearer]',
        'GET  /api/v1/auth/me                  [Bearer]',
        'GET  /api/v1/auth/users               [Public]',
        'GET  /api/v1/auth/trust-score/{id}    [Public]',
        'GET  /api/v1/auth/users/trust-score   [Query: user_id]',
        'POST /api/v1/auth/trust-score/update  [Public/Bearer]'
    ]
], 404);

// ── 6. Helper: Phân hạng Tier tín nhiệm ───────────────────────────────────────
function evaluateTier(int $score): string
{
    return match (true) {
        $score >= 800 => 'KIM CƯƠNG (Miễn cọc 100% & Ưu tiên Barter)',
        $score >= 600 => 'VÀNG (Ưu tiên Barter & Giảm 50% cọc)',
        $score >= 400 => 'BẠC (Sinh viên uy tín tiêu chuẩn)',
        $score >= 200 => 'ĐỒNG (Cần tích lũy thêm giao dịch)',
        default       => 'CẢNH BÁO (Hạn chế quyền trao đổi đồ)'
    };
}
