<?php

namespace App\Services;

/**
 * DYNAMIC TOTP QR CODE ENGINE
 * Sinh và kiểm tra mã QR động bảo mật có thời hạn 30 giây cho trạm giao dịch Hub
 */
class DynamicQREngine
{
    private string $secretKey;
    private int $timeStep; // 30 giây

    public function __construct(string $secretKey = 'HUNRE_O2O_SECRET_KEY_2026', int $timeStep = 30)
    {
        $this->secretKey = $secretKey;
        $this->timeStep = $timeStep;
    }

    /**
     * Sinh mã Token động dựa trên OrderCode và cửa sổ thời gian (Time Window)
     */
    public function generateToken(string $orderCode, int $userId, string $role = 'BUYER'): array
    {
        $currentTime = time();
        $timeWindow = floor($currentTime / $this->timeStep);
        
        $payload = "{$orderCode}|{$userId}|{$role}|{$timeWindow}";
        $hash = hash_hmac('sha256', $payload, $this->secretKey);
        $token = strtoupper(substr($hash, 0, 16)); // 16 ký tự mã xác nhận

        $secondsRemaining = $this->timeStep - ($currentTime % $this->timeStep);

        return [
            'order_code'        => $orderCode,
            'role'              => $role,
            'token'             => $token,
            'expires_in_seconds'=> $secondsRemaining,
            'qr_payload'        => "HUNRE:{$orderCode}:{$userId}:{$role}:{$token}"
        ];
    }

    /**
     * Nhân viên trạm Hub giải mã và kiểm tra tính hợp lệ của mã QR (Cho phép sai số ±1 time window)
     */
    public function verifyToken(string $orderCode, int $userId, string $role, string $tokenToVerify): bool
    {
        $currentTime = time();
        $currentWindow = floor($currentTime / $this->timeStep);

        // Chấp nhận cửa sổ thời gian hiện tại và cửa sổ trước đó 30s phòng trường hợp lệch đồng hồ
        for ($offset = -1; $offset <= 0; $offset++) {
            $window = $currentWindow + $offset;
            $payload = "{$orderCode}|{$userId}|{$role}|{$window}";
            $expectedHash = strtoupper(substr(hash_hmac('sha256', $payload, $this->secretKey), 0, 16));
            if (hash_equals($expectedHash, $tokenToVerify)) {
                return true;
            }
        }

        return false;
    }
}
