<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\TrustScoreController;

/*
|--------------------------------------------------------------------------
| AUTH SERVICE API ROUTES
| Microservice: Identity, Student KYC & Trust Score Engine
|--------------------------------------------------------------------------
*/

Route::prefix('v1/auth')->group(function () {
    // Đăng ký tài khoản sinh viên HUNRE (yêu cầu email @hunre.edu.vn)
    Route::post('/register', [AuthController::class, 'register']);
    
    // Đăng nhập cấp phát JWT Token
    Route::post('/login', [AuthController::class, 'login']);
    
    // Lấy thông tin cá nhân & Điểm Uy Tín (Yêu cầu JWT)
    Route::middleware('auth:api')->group(function () {
        Route::get('/me', [AuthController::class, 'me']);
        Route::post('/logout', [AuthController::class, 'logout']);
        
        // Quản lý Điểm Uy Tín Sinh Viên (Trust Score)
        Route::get('/trust-score/{userId}', [TrustScoreController::class, 'getScore']);
        Route::post('/trust-score/update', [TrustScoreController::class, 'updateScore']);
    });
});
