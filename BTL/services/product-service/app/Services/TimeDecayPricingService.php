<?php

namespace App\Services;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

/**
 * SERVICE QUẢN LÝ ĐẤU GIÁ NGƯỢC (TIME-DECAY PRICING CRONJOB)
 * Tự động hạ giá sản phẩm cần thanh lý gấp cuối kỳ theo thời gian
 */
class TimeDecayPricingService
{
    /**
     * Quét toàn bộ sản phẩm đang bật chế độ is_time_decay và cập nhật giá mới
     */
    public function executeDecayBatch(): int
    {
        $products = DB::table('products')
            ->where('status', 'ACTIVE')
            ->where('is_time_decay', 1)
            ->whereColumn('current_price', '>', 'floor_price')
            ->get();

        $updatedCount = 0;

        foreach ($products as $product) {
            $createdTime = strtotime($product->created_at);
            $hoursElapsed = (time() - $createdTime) / 3600;

            // Nếu người bán cài đặt mức giảm cố định mỗi giờ
            if ($product->decay_rate_per_hour > 0) {
                $reduction = $hoursElapsed * $product->decay_rate_per_hour;
                $newPrice = max($product->floor_price, $product->original_price - $reduction);
            } else {
                // Mặc định: Giảm 5% mỗi 12 giờ cho đến khi chạm giá sàn
                $intervals = floor($hoursElapsed / 12);
                $reduction = $product->original_price * (0.05 * $intervals);
                $newPrice = max($product->floor_price, $product->original_price - $reduction);
            }

            $newPrice = round($newPrice, -3); // Làm tròn đến nghìn đồng

            if ($newPrice != $product->current_price) {
                DB::table('products')->where('id', $product->id)->update([
                    'current_price' => $newPrice,
                    'updated_at'    => now()
                ]);
                $updatedCount++;
                Log::info("Time-decay: Cập nhật sản phẩm #{$product->id} - Giá cũ: {$product->current_price} -> Giá mới: {$newPrice}");
            }
        }

        return $updatedCount;
    }
}
