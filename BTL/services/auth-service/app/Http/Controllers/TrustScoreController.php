<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\TrustScoreService;
use Illuminate\Support\Facades\DB;

/**
 * TRUST SCORE CONTROLLER
 * Tra cứu và cập nhật Điểm Uy Tín sinh viên trong hệ sinh thái HUNRE
 */
class TrustScoreController
{
    protected TrustScoreService $trustScoreService;

    public function __construct(TrustScoreService $trustScoreService)
    {
        $this->trustScoreService = $trustScoreService;
    }

    /**
     * Tra cứu điểm uy tín và phân hạng sinh viên
     */
    public function getScore(int $userId)
    {
        $user = DB::table('users')->where('id', $userId)->first();
        if (!$user) {
            return response()->json(['success' => false, 'message' => 'Không tìm thấy sinh viên.'], 404);
        }

        $tier = $this->trustScoreService->determineTier($user->trust_score);

        return response()->json([
            'success' => true,
            'data'    => [
                'user_id'      => $user->id,
                'full_name'    => $user->full_name,
                'student_code' => $user->student_code,
                'trust_score'  => $user->trust_score,
                'tier'         => $tier,
                'benefits'     => [
                    'can_barter'        => $user->trust_score >= 200,
                    'deposit_discount'  => $user->trust_score >= 600 ? '50%' : ($user->trust_score >= 800 ? '100%' : '0%'),
                    'priority_matching' => $user->trust_score >= 600
                ]
            ]
        ]);
    }

    /**
     * Cập nhật điểm uy tín theo sự kiện nghiệp vụ
     */
    public function updateScore(Request $request)
    {
        $validated = $request->validate([
            'user_id'      => 'required|integer',
            'score_change' => 'required|integer',
            'reason'       => 'required|string',
            'order_id'     => 'nullable|integer'
        ]);

        try {
            $result = $this->trustScoreService->recordScoreChange(
                $validated['user_id'],
                $validated['score_change'],
                $validated['reason'],
                $validated['order_id'] ?? null
            );

            return response()->json([
                'success' => true,
                'message' => 'Cập nhật điểm uy tín thành công!',
                'data'    => $result
            ]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}
