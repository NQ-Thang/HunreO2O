<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;

/**
 * HUNRE TRUST SCORE ENGINE
 * Quản lý & tính toán Điểm Uy Tín của sinh viên trong hệ sinh thái O2O
 */
class TrustScoreService
{
    // Hằng số cộng/trừ điểm theo hành vi
    public const EVENT_O2O_SUCCESS_ON_TIME   = 5;   // Giao dịch tại Hub thành công đúng hẹn (+5)
    public const EVENT_RECEIVE_5_STAR_RATING  = 2;   // Được người mua đánh giá 5 sao (+2)
    public const EVENT_CANCEL_AFTER_MATCH    = -20; // Hủy kèo sau khi đã ghép cặp thành công (-20)
    public const EVENT_HUB_DEFECT_DISCREPANCY = -30; // Khai báo gian lận tình trạng đồ bị Hub phát hiện (-30)
    public const EVENT_MISSED_HUB_DEADLINE   = -15; // Quá hạn không mang đồ ra Trạm Hub (-15)

    /**
     * Cập nhật điểm uy tín kèm ghi log lịch sử thay đổi
     */
    public function recordScoreChange(int $userId, int $scoreChange, string $reason, ?int $orderId = null): array
    {
        return DB::transaction(function () use ($userId, $scoreChange, $reason, $orderId) {
            $user = DB::table('users')->where('id', $userId)->lockForUpdate()->first();
            if (!$user) {
                throw new \Exception("Không tìm thấy sinh viên ID: {$userId}");
            }

            // Điểm uy tín nằm trong khoảng [0, 1000]
            $newScore = max(0, min(1000, $user->trust_score + $scoreChange));

            DB::table('users')->where('id', $userId)->update([
                'trust_score' => $newScore,
                'updated_at'  => now()
            ]);

            // Xác định phân hạng tín nhiệm sinh viên (Tier)
            $tier = $this->determineTier($newScore);

            return [
                'user_id'     => $userId,
                'old_score'   => $user->trust_score,
                'score_change'=> $scoreChange,
                'new_score'   => $newScore,
                'tier'        => $tier,
                'reason'      => $reason
            ];
        });
    }

    /**
     * Xác định phân hạng danh hiệu sinh viên HUNRE
     */
    public function determineTier(int $score): string
    {
        if ($score >= 800) return 'KIM CƯƠNG (Bảo chứng 100% không cần cọc)';
        if ($score >= 600) return 'VÀNG (Ưu tiên ghép Barter Graph & Giảm 50% cọc)';
        if ($score >= 400) return 'BẠC (Sinh viên uy tín tiêu chuẩn)';
        if ($score >= 200) return 'ĐỒNG (Cần đặt cọc 100% khi mua)';
        return 'CẢNH BÁO (Hạn chế quyền trao đổi đồ)';
    }
}
