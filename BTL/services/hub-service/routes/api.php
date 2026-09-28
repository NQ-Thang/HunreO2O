<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HubController;

/*
|--------------------------------------------------------------------------
| HUB SERVICE API ROUTES
| Microservice: O2O Physical Hubs, Locker Grid & Dynamic TOTP QR Code
|--------------------------------------------------------------------------
*/

Route::prefix('v1/hub')->group(function () {
    // Danh sách các trạm Hub (CS1 Hà Nội, CS2 Thanh Hóa)
    Route::get('/stations', [HubController::class, 'getHubs']);
    
    // Tình trạng ô tủ Locker tại trạm
    Route::get('/lockers/{hubId}', [HubController::class, 'getLockers']);
    
    // Sinh mã QR động (TOTP HMAC SHA-256 xoay mỗi 30s) cho người bán/mua
    Route::get('/orders/{orderCode}/dynamic-qr', [HubController::class, 'generateDynamicQR']);
    
    // Nhân viên Trạm Hub quét mã QR bàn giao / nhận đồ
    Route::post('/scan-checkin', [HubController::class, 'processCheckin']);
    Route::post('/scan-checkout', [HubController::class, 'processCheckout']);
});
