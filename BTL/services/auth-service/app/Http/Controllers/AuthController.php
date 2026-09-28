<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

/**
 * AUTH CONTROLLER (HUNRE IDENTITY & KYC)
 * Xác thực sinh viên đại học HUNRE qua email trường @hunre.edu.vn
 */
class AuthController
{
    /**
     * Đăng ký tài khoản sinh viên HUNRE
     */
    public function register(Request $request)
    {
        $validated = $request->validate([
            'student_code' => 'required|string|unique:users,student_code',
            'full_name'    => 'required|string|max:100',
            'email'        => 'required|email|unique:users,email',
            'password'     => 'required|string|min:6',
            'faculty'      => 'nullable|string',
            'campus'       => 'nullable|in:CS1_HA_NOI,CS2_THANH_HOA'
        ]);

        // Kiểm tra bắt buộc email phải thuộc domain Đại học HUNRE
        if (!str_ends_with(strtolower($validated['email']), '@hunre.edu.vn')) {
            return response()->json([
                'success' => false,
                'message' => 'Lỗi xác thực KYC: Chỉ chấp nhận email định danh sinh viên Đại học Tài nguyên và Môi trường Hà Nội (@hunre.edu.vn)!'
            ], 422);
        }

        $userId = DB::table('users')->insertGetId([
            'student_code'  => $validated['student_code'],
            'full_name'     => $validated['full_name'],
            'email'         => strtolower($validated['email']),
            'password_hash' => Hash::make($validated['password']),
            'faculty'       => $validated['faculty'] ?? 'Công nghệ Thông tin',
            'campus'        => $validated['campus'] ?? 'CS1_HA_NOI',
            'trust_score'   => 100, // Điểm uy tín khởi tạo
            'kyc_status'    => 'VERIFIED',
            'role'          => 'STUDENT',
            'wallet_balance'=> 0.00,
            'created_at'    => now(),
            'updated_at'    => now()
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đăng ký tài khoản sinh viên HUNRE thành công!',
            'data'    => [
                'user_id'      => $userId,
                'student_code' => $validated['student_code'],
                'full_name'    => $validated['full_name'],
                'email'        => $validated['email'],
                'trust_score'  => 100
            ]
        ], 201);
    }

    /**
     * Đăng nhập sinh viên HUNRE & cấp token
     */
    public function login(Request $request)
    {
        $validated = $request->validate([
            'email'    => 'required|email',
            'password' => 'required|string'
        ]);

        $user = DB::table('users')->where('email', strtolower($validated['email']))->first();

        if (!$user || !Hash::check($validated['password'], $user->password_hash)) {
            return response()->json([
                'success' => false,
                'message' => 'Email hoặc mật khẩu không chính xác.'
            ], 401);
        }

        // Sinh JWT token giả lập / thực tế
        $token = "HUNRE_JWT_" . bin2hex(random_bytes(24));

        return response()->json([
            'success' => true,
            'message' => 'Đăng nhập thành công!',
            'token'   => $token,
            'user'    => [
                'id'           => $user->id,
                'student_code' => $user->student_code,
                'full_name'    => $user->full_name,
                'email'        => $user->email,
                'trust_score'  => $user->trust_score,
                'campus'       => $user->campus,
                'role'         => $user->role,
                'wallet_balance' => (float) $user->wallet_balance
            ]
        ]);
    }

    /**
     * Lấy thông tin cá nhân hiện tại
     */
    public function me(Request $request)
    {
        // Giả lập user lấy từ auth token
        $user = DB::table('users')->where('id', 1)->first();

        return response()->json([
            'success' => true,
            'user'    => $user
        ]);
    }
}
