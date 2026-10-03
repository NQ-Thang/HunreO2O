<?php

declare(strict_types=1);

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Exception;

/**
 * HUNRE TRUST SCORE ENGINE
 * Quản lý & tính toán Điểm Uy Tín của sinh viên trong hệ sinh thái O2O & Trao đổi đồ HUNRE.
 */
class TrustScoreService
{
    // Hằng số điểm cộng / trừ theo sự kiện nghiệp vụ O2O
    public const EVENT_O2O_SUCCESS_ON_TIME    = 5;   // Giao dịch tại Hub thành công đúng hẹn (+5)
    public const EVENT_RECEIVE_5_STAR_RATING  = 2;   // Được người mua đánh giá 5 sao (+2)
    public const EVENT_CANCEL_AFTER_MATCH     = -20; // Hủy kèo sau khi đã ghép cặp thành công (-20)
    public const EVENT_HUB_DEFECT_DISCREPANCY  = -30; // Khai báo gian lận tình trạng đồ bị Hub phát hiện (-30)
    public const EVENT_MISSED_HUB_DEADLINE    = -15; // Quá hạn không mang đồ ra Trạm Hub (-15)

    /**
     * Cập nhật điểm uy tín kèm giao dịch an toàn và ghi nhận thay đổi
     *
     * @param int $userId ID sinh viên
     * @param int $scoreChange Số điểm thay đổi (âm hoặc dương)
     * @param string $reason Lý do cập nhật điểm
     * @param int|null $orderId ID đơn hàng liên quan (nếu có)
     * @return array Dữ liệu kết quả sau cập nhật
     * @throws Exception
     */
    public function recordScoreChange(int $userId, int $scoreChange, string $reason, ?int $orderId = null): array
    {
        return DB::transaction(function () use ($userId, $scoreChange, $reason, $orderId) {
            $user = DB::table('users')->where('id', $userId)->lockForUpdate()->first();
            if (!$user) {
                throw new Exception("Không tìm thấy sinh viên ID: {$userId}");
            }

            $oldScore = (int) $user->trust_score;
            // Điểm uy tín nằm trong khoảng chuẩn [0, 1000]
            $newScore = max(0, min(1000, $oldScore + $scoreChange));

            DB::table('users')->where('id', $userId)->update([
                'trust_score' => $newScore,
                'updated_at'  => now()
            ]);

            $tier     = $this->determineTier($newScore);
            $benefits = $this->getBenefits($newScore);

            return [
                'user_id'      => $userId,
                'old_score'    => $oldScore,
                'score_change' => $scoreChange,
                'new_score'    => $newScore,
                'tier'         => $tier,
                'reason'       => $reason,
                'benefits'     => $benefits
            ];
        });
    }

    /**
     * Phân loại danh hiệu và thứ hạng sinh viên HUNRE dựa trên điểm uy tín (O(1) Match Expression)
     */
    public function determineTier(int $score): string
    {
        return match (true) {
            $score >= 800 => 'KIM CƯƠNG (Miễn cọc 100% & Ưu tiên Barter)',
            $score >= 600 => 'VÀNG (Ưu tiên Barter & Giảm 50% cọc)',
            $score >= 400 => 'BẠC (Sinh viên uy tín tiêu chuẩn)',
            $score >= 200 => 'ĐỒNG (Cần tích lũy thêm giao dịch)',
            default       => 'CẢNH BÁO (Hạn chế quyền trao đổi đồ)'
        };
    }

    /**
     * Trả về danh sách đặc quyền (Benefits) tương ứng với số điểm uy tín
     */
    public function getBenefits(int $score): array
    {
        return [
            'can_barter'        => $score >= 200,
            'deposit_discount'  => $score >= 800 ? '100%' : ($score >= 600 ? '50%' : '0%'),
            'priority_matching' => $score >= 600,
            'fee_waiver'        => $score >= 800
        ];
    }
}
