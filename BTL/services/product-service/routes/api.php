<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ProductController;

/*
|--------------------------------------------------------------------------
| PRODUCT SERVICE API ROUTES
| Microservice: Catalog, Postings, AI Inspection Link & Time-decay Pricing
|--------------------------------------------------------------------------
*/

Route::prefix('v1/products')->group(function () {
    // Danh sách sản phẩm, lọc theo danh mục, tìm kiếm
    Route::get('/', [ProductController::class, 'index']);
    
    // Chi tiết sản phẩm kèm báo cáo thẩm định AI
    Route::get('/{id}', [ProductController::class, 'show']);
    
    // Đăng bán sản phẩm (gọi ngầm AI Service thẩm định ảnh)
    Route::post('/', [ProductController::class, 'store']);
    
    // Đăng ký tham gia vòng tròn trao đổi đồ (Barter Graph)
    Route::post('/{id}/opt-in-barter', [ProductController::class, 'optInBarter']);
    
    // Kích hoạt tính năng tự động hạ giá theo giờ (Time-decay pricing)
    Route::post('/{id}/enable-time-decay', [ProductController::class, 'enableTimeDecay']);
});
