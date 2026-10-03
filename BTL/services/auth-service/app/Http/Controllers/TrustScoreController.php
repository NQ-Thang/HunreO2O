<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use App\Services\TrustScoreService;
use Illuminate\Support\Facades\DB;
use Throwable;

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
     * Tra cứu điểm uy tín và phân hạng danh hiệu sinh viên
     */
    public function getScore(int $userId): JsonResponse
    {
        $user = DB::table('users')->where('id', $userId)->first();
        if (!$user) {
            return response()->json([
                'success' => false, 
                'message' => 'Không tìm thấy sinh viên trong hệ thống.'
            ], 404);
        }

        $score    = (int) $user->trust_score;
        $tier     = $this->trustScoreService->determineTier($score);
        $benefits = $this->trustScoreService->getBenefits($score);

        return response()->json([
            'success' => true,
            'data'    => [
                'user_id'        => (int) $user->id,
                'full_name'      => $user->full_name,
                'student_code'   => $user->student_code,
                'trust_score'    => $score,
                'tier'           => $tier,
                'wallet_balance' => (float) ($user->wallet_balance ?? 0.0),
                'campus'         => $user->campus ?? 'CS1_HA_NOI',
                'benefits'       => $benefits
            ]
        ]);
    }

    /**
     * Cập nhật điểm uy tín theo sự kiện nghiệp vụ
     */
    public function updateScore(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'user_id'      => 'required|integer',
            'score_change' => 'required|integer',
            'reason'       => 'required|string|max:255',
            'order_id'     => 'nullable|integer'
        ]);

        try {
            $result = $this->trustScoreService->recordScoreChange(
                (int) $validated['user_id'],
                (int) $validated['score_change'],
                (string) $validated['reason'],
                isset($validated['order_id']) ? (int) $validated['order_id'] : null
            );

            return response()->json([
                'success' => true,
                'message' => 'Cập nhật điểm uy tín thành công!',
                'data'    => $result
            ]);
        } catch (Throwable $e) {
            return response()->json([
                'success' => false, 
                'message' => $e->getMessage()
            ], 500);
        }
    }
}
