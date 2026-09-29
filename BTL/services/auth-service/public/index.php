<?php
/**
 * HUNRE AUTH SERVICE - Entry Point & Router
 * Port: 8001 | PHP Built-in Server
 *
 * Routes:
 *   POST   /api/v1/auth/register
 *   POST   /api/v1/auth/login
 *   POST   /api/v1/auth/logout              [Auth Required]
 *   GET    /api/v1/auth/me                  [Auth Required]
 *   GET    /api/v1/auth/trust-score/{id}    [Auth Required]
 *   POST   /api/v1/auth/trust-score/update  [Auth Required]
 *   GET    /health
 */

// ── CORS Headers (luôn gửi trước) ─────────────────────────────────────────
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

// ── Load helpers & config ──────────────────────────────────────────────────
require_once __DIR__ . '/../app/config.php';

// ── Parse request ─────────────────────────────────────────────────────────
$method = $_SERVER['REQUEST_METHOD'];
$uri    = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$uri    = rtrim($uri, '/');

$body = [];
$raw  = file_get_contents('php://input');
if ($raw) {
    $body = json_decode($raw, true) ?? [];
}

// ── Router ────────────────────────────────────────────────────────────────

// Health check
if ($uri === '/health' || $uri === '') {
    jsonResponse([
        'service' => 'HUNRE Auth & Trust Score Service',
        'version' => '3.0.0',
        'status'  => 'UP',
        'endpoints' => [
            'POST /api/v1/auth/register',
            'POST /api/v1/auth/login',
            'POST /api/v1/auth/logout         [Bearer]',
            'GET  /api/v1/auth/me             [Bearer]',
            'GET  /api/v1/auth/trust-score/{id} [Bearer]',
            'POST /api/v1/auth/trust-score/update [Bearer]',
        ]
    ]);
}

// ── POST /api/v1/auth/register ────────────────────────────────────────────
if ($uri === '/api/v1/auth/register' && $method === 'POST') {
    $studentCode = trim($body['student_code'] ?? '');
    $fullName    = trim($body['full_name'] ?? '');
    $email       = strtolower(trim($body['email'] ?? ''));
    $password    = $body['password'] ?? '';
    $faculty     = trim($body['faculty'] ?? 'Công nghệ Thông tin');
    $campus      = $body['campus'] ?? 'CS1_HA_NOI';

    // Validation
    if (!$studentCode || !$fullName || !$email || !$password) {
        jsonResponse(['success' => false, 'message' => 'Thiếu các trường bắt buộc: student_code, full_name, email, password.'], 422);
    }
    if (strlen($password) < 6) {
        jsonResponse(['success' => false, 'message' => 'Mật khẩu phải có ít nhất 6 ký tự.'], 422);
    }

    // Bắt buộc email @hunre.edu.vn (KYC Domain Check)
    if (!str_ends_with($email, '@hunre.edu.vn')) {
        jsonResponse(['success' => false, 'message' => 'Lỗi KYC: Chỉ chấp nhận email sinh viên Đại học Tài nguyên và Môi trường Hà Nội (@hunre.edu.vn).'], 422);
    }

    $validCampuses = ['CS1_HA_NOI', 'CS2_THANH_HOA'];
    if (!in_array($campus, $validCampuses)) $campus = 'CS1_HA_NOI';

    $db = getDB();

    // Kiểm tra trùng
    $dup = $db->prepare("SELECT id FROM users WHERE email = ? OR student_code = ? LIMIT 1");
    $dup->execute([$email, $studentCode]);
    if ($dup->fetch()) {
        jsonResponse(['success' => false, 'message' => 'Email hoặc mã sinh viên đã được đăng ký.'], 409);
    }

    $stmt = $db->prepare("
        INSERT INTO users (student_code, full_name, email, password_hash, faculty, campus, trust_score, kyc_status, role, wallet_balance, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 100, 'VERIFIED', 'STUDENT', 0.00, NOW(), NOW())
    ");
    $stmt->execute([$studentCode, $fullName, $email, password_hash(PASSWORD_BCRYPT, $password), $faculty, $campus]);
    $userId = (int) $db->lastInsertId();

    jsonResponse([
        'success' => true,
        'message' => 'Đăng ký tài khoản sinh viên HUNRE thành công!',
        'data'    => [
            'user_id'      => $userId,
            'student_code' => $studentCode,
            'full_name'    => $fullName,
            'email'        => $email,
            'trust_score'  => 100,
        ]
    ], 201);
}

// ── POST /api/v1/auth/login ───────────────────────────────────────────────
if ($uri === '/api/v1/auth/login' && $method === 'POST') {
    $email    = strtolower(trim($body['email'] ?? ''));
    $password = $body['password'] ?? '';

    if (!$email || !$password) {
        jsonResponse(['success' => false, 'message' => 'Vui lòng nhập email và mật khẩu.'], 422);
    }

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE email = ? LIMIT 1");
    $stmt->execute([$email]);
    $user = $stmt->fetch();

    if (!$user || !password_verify($password, $user->password_hash)) {
        jsonResponse(['success' => false, 'message' => 'Email hoặc mật khẩu không chính xác.'], 401);
    }

    // Tạo Bearer token ngẫu nhiên (64 ký tự hex)
    $rawToken  = bin2hex(random_bytes(32));                  // 64-char hex string
    $tokenHash = hash('sha256', $rawToken);                  // Lưu hash, KHÔNG lưu raw
    $prefix    = substr($rawToken, 0, 12);                   // Prefix để debug/log
    $expiresAt = date('Y-m-d H:i:s', time() + 86400);       // Hết hạn sau 24h

    // Hủy token cũ của user này (1 user = 1 active token)
    $db->prepare("DELETE FROM api_tokens WHERE user_id = ?")->execute([$user->id]);

    // Lưu token mới
    $db->prepare("
        INSERT INTO api_tokens (user_id, token_hash, token_prefix, expires_at, created_at)
        VALUES (?, ?, ?, ?, NOW())
    ")->execute([$user->id, $tokenHash, $prefix, $expiresAt]);

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
            'trust_score'    => (int) $user->trust_score,
            'campus'         => $user->campus,
            'role'           => $user->role,
            'wallet_balance' => (float) $user->wallet_balance,
        ]
    ]);
}

// ── POST /api/v1/auth/logout ──────────────────────────────────────────────
if ($uri === '/api/v1/auth/logout' && $method === 'POST') {
    $authUser = requireAuth();
    $db       = getDB();

    $rawToken  = getBearerToken();
    $tokenHash = hash('sha256', $rawToken);
    $db->prepare("DELETE FROM api_tokens WHERE token_hash = ?")->execute([$tokenHash]);

    jsonResponse(['success' => true, 'message' => 'Đăng xuất thành công. Token đã bị thu hồi.']);
}

// ── GET /api/v1/auth/me ───────────────────────────────────────────────────
if ($uri === '/api/v1/auth/me' && $method === 'GET') {
    $authUser = requireAuth(); // Lấy user từ token → KHÔNG hardcode id

    $tier = determineTier((int) $authUser->trust_score);

    jsonResponse([
        'success' => true,
        'user'    => [
            'id'                    => (int) $authUser->id,
            'student_code'          => $authUser->student_code,
            'full_name'             => $authUser->full_name,
            'email'                 => $authUser->email,
            'phone'                 => $authUser->phone,
            'campus'                => $authUser->campus,
            'faculty'               => $authUser->faculty,
            'role'                  => $authUser->role,
            'trust_score'           => (int) $authUser->trust_score,
            'trust_tier'            => $tier,
            'kyc_status'            => $authUser->kyc_status,
            'wallet_balance'        => (float) $authUser->wallet_balance,
            'escrow_locked_balance' => (float) $authUser->escrow_locked_balance,
        ]
    ]);
}

// ── GET /api/v1/auth/trust-score/{userId} ────────────────────────────────
if (preg_match('#^/api/v1/auth/trust-score/(\d+)$#', $uri, $m) && $method === 'GET') {
    requireAuth();
    $userId = (int) $m[1];

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ? LIMIT 1");
    $stmt->execute([$userId]);
    $user = $stmt->fetch();

    if (!$user) {
        jsonResponse(['success' => false, 'message' => 'Không tìm thấy sinh viên.'], 404);
    }

    $tier = determineTier((int) $user->trust_score);

    jsonResponse([
        'success' => true,
        'data'    => [
            'user_id'      => (int) $user->id,
            'full_name'    => $user->full_name,
            'student_code' => $user->student_code,
            'trust_score'  => (int) $user->trust_score,
            'tier'         => $tier,
            'benefits'     => [
                'can_barter'        => $user->trust_score >= 200,
                'deposit_discount'  => $user->trust_score >= 800 ? '100%' : ($user->trust_score >= 600 ? '50%' : '0%'),
                'priority_matching' => $user->trust_score >= 600,
            ]
        ]
    ]);
}

// ── POST /api/v1/auth/trust-score/update ─────────────────────────────────
if ($uri === '/api/v1/auth/trust-score/update' && $method === 'POST') {
    requireAuth();

    $userId      = (int) ($body['user_id'] ?? 0);
    $scoreChange = (int) ($body['score_change'] ?? 0);
    $reason      = trim($body['reason'] ?? '');

    if (!$userId || !$scoreChange || !$reason) {
        jsonResponse(['success' => false, 'message' => 'Thiếu trường bắt buộc: user_id, score_change, reason.'], 422);
    }

    $db   = getDB();
    $stmt = $db->prepare("SELECT * FROM users WHERE id = ? LIMIT 1");
    $stmt->execute([$userId]);
    $user = $stmt->fetch();

    if (!$user) {
        jsonResponse(['success' => false, 'message' => 'Không tìm thấy sinh viên.'], 404);
    }

    $oldScore = (int) $user->trust_score;
    $newScore = max(0, min(1000, $oldScore + $scoreChange)); // Giới hạn [0, 1000]

    $db->prepare("UPDATE users SET trust_score = ?, updated_at = NOW() WHERE id = ?")->execute([$newScore, $userId]);

    jsonResponse([
        'success' => true,
        'message' => 'Cập nhật điểm uy tín thành công!',
        'data'    => [
            'user_id'      => $userId,
            'old_score'    => $oldScore,
            'score_change' => $scoreChange,
            'new_score'    => $newScore,
            'tier'         => determineTier($newScore),
            'reason'       => $reason,
        ]
    ]);
}

// ── 404 Fallback ──────────────────────────────────────────────────────────
jsonResponse([
    'success' => false,
    'message' => "Route không tồn tại: [{$method}] {$uri}",
    'available_routes' => [
        'POST /api/v1/auth/register',
        'POST /api/v1/auth/login',
        'POST /api/v1/auth/logout         [Bearer]',
        'GET  /api/v1/auth/me             [Bearer]',
        'GET  /api/v1/auth/trust-score/{id} [Bearer]',
        'POST /api/v1/auth/trust-score/update [Bearer]',
    ]
], 404);

// ── Helper functions ──────────────────────────────────────────────────────
function determineTier(int $score): string
{
    if ($score >= 800) return 'KIM CƯƠNG (Bảo chứng 100% không cần cọc)';
    if ($score >= 600) return 'VÀNG (Ưu tiên ghép Barter Graph & Giảm 50% cọc)';
    if ($score >= 400) return 'BẠC (Sinh viên uy tín tiêu chuẩn)';
    if ($score >= 200) return 'ĐỒNG (Cần đặt cọc 100% khi mua)';
    return 'CẢNH BÁO (Hạn chế quyền trao đổi đồ)';
}
