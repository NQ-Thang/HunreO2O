<?php
/**
 * HUNRE Auth Service - Cấu hình trung tâm
 * Đọc biến môi trường từ Docker (hoặc file .env nếu chạy local)
 */

// Load .env file nếu tồn tại (dùng khi chạy local không qua Docker)
$envFile = __DIR__ . '/../.env';
if (file_exists($envFile)) {
    $lines = file($envFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (str_starts_with(trim($line), '#') || !str_contains($line, '=')) continue;
        [$key, $value] = explode('=', $line, 2);
        $_ENV[trim($key)] = trim($value);
    }
}

/**
 * Lấy biến môi trường với giá trị mặc định
 */
function env(string $key, mixed $default = null): mixed
{
    return $_ENV[$key] ?? getenv($key) ?: $default;
}

/**
 * Kết nối PDO đến MySQL (Singleton per request)
 */
function getDB(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $host     = env('DB_HOST', '127.0.0.1');
        $port     = env('DB_PORT', '3306');
        $database = env('DB_DATABASE', 'hunre_ecommerce');
        $username = env('DB_USERNAME', 'root');
        $password = env('DB_PASSWORD', 'root');

        $dsn = "mysql:host={$host};port={$port};dbname={$database};charset=utf8mb4";
        $pdo = new PDO($dsn, $username, $password, [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ,
            PDO::ATTR_EMULATE_PREPARES   => false,
        ]);
    }
    return $pdo;
}

/**
 * Trả về JSON response và dừng script
 */
function jsonResponse(mixed $data, int $statusCode = 200): never
{
    http_response_code($statusCode);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

/**
 * Lấy Bearer token từ Authorization header
 */
function getBearerToken(): ?string
{
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? '';
    if (preg_match('/^Bearer\s+(\S+)$/i', trim($header), $matches)) {
        return $matches[1];
    }
    return null;
}

/**
 * Xác thực Bearer token và trả về user object.
 * Nếu không hợp lệ, trả 401 và dừng.
 */
function requireAuth(): object
{
    $rawToken = getBearerToken();
    if (!$rawToken) {
        jsonResponse(['success' => false, 'message' => 'Unauthorized: Thiếu Authorization header.'], 401);
    }

    $tokenHash = hash('sha256', $rawToken);
    $db = getDB();

    $stmt = $db->prepare("
        SELECT t.id AS token_id, t.user_id, t.expires_at, u.*
        FROM api_tokens t
        JOIN users u ON u.id = t.user_id
        WHERE t.token_hash = ?
          AND t.expires_at > NOW()
        LIMIT 1
    ");
    $stmt->execute([$tokenHash]);
    $result = $stmt->fetch();

    if (!$result) {
        jsonResponse(['success' => false, 'message' => 'Unauthorized: Token không hợp lệ hoặc đã hết hạn.'], 401);
    }

    // Cập nhật last_used_at
    $db->prepare("UPDATE api_tokens SET last_used_at = NOW() WHERE id = ?")->execute([$result->token_id]);

    return $result;
}
