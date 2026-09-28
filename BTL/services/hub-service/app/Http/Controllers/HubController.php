<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\DynamicQREngine;
use Illuminate\Support\Facades\DB;

/**
 * HUB CONTROLLER
 * Quản lý Trạm trung gian O2O, Ô tủ Locker thông minh & Quét mã TOTP QR bảo mật
 */
class HubController
{
    protected DynamicQREngine $qrEngine;

    public function __construct(DynamicQREngine $qrEngine)
    {
        $this->qrEngine = $qrEngine;
    }

    /**
     * Danh sách các Trạm Hub trong khuôn viên HUNRE
     */
    public function getHubs()
    {
        $hubs = DB::table('hubs')->get();
        return response()->json(['success' => true, 'data' => $hubs]);
    }

    /**
     * Tình trạng ô tủ Locker tại một Trạm Hub
     */
    public function getLockers(int $hubId)
    {
        $lockers = DB::table('lockers')->where('hub_id', $hubId)->get();
        return response()->json(['success' => true, 'data' => $lockers]);
    }

    /**
     * Sinh mã Dynamic TOTP QR có hạn 30s cho người bán/người mua
     */
    public function generateDynamicQR(Request $request, string $orderCode)
    {
        $userId = $request->query('user_id', 1);
        $role = $request->query('role', 'BUYER'); // BUYER hoặc SELLER

        $qrData = $this->qrEngine->generateToken($orderCode, (int) $userId, $role);

        return response()->json([
            'success' => true,
            'data'    => $qrData
        ]);
    }

    /**
     * Nhân viên Trạm Hub quét mã CHECK-IN (Người bán đến gửi đồ vào Hub)
     */
    public function processCheckin(Request $request)
    {
        $validated = $request->validate([
            'order_code'  => 'required|string',
            'token'       => 'required|string',
            'seller_id'   => 'required|integer',
            'size_type'   => 'nullable|in:SMALL,MEDIUM,LARGE'
        ]);

        // 1. Xác thực mã QR TOTP
        $isValid = $this->qrEngine->verifyToken($validated['order_code'], $validated['seller_id'], 'SELLER', $validated['token']);
        if (!$isValid) {
            return response()->json(['success' => false, 'message' => 'Mã QR đã hết hạn hoặc không hợp lệ.'], 400);
        }

        $order = DB::table('escrow_orders')->where('order_code', $validated['order_code'])->first();
        if (!$order) {
            return response()->json(['success' => false, 'message' => 'Không tìm thấy đơn hàng.'], 404);
        }

        // 2. Tự động tìm một ô tủ trống tại Hub để gán cho đơn hàng
        $emptyLocker = DB::table('lockers')
            ->where('hub_id', $order->hub_id)
            ->where('status', 'EMPTY')
            ->first();

        if (!$emptyLocker) {
            return response()->json(['success' => false, 'message' => 'Hiện tại Trạm Hub đã hết ô tủ trống. Vui lòng liên hệ thủ kho.'], 500);
        }

        // 3. Khóa ô tủ & Cập nhật đơn hàng
        DB::table('lockers')->where('id', $emptyLocker->id)->update([
            'status'           => 'OCCUPIED',
            'current_order_id' => $order->id
        ]);

        DB::table('escrow_orders')->where('id', $order->id)->update([
            'locker_id'   => $emptyLocker->id,
            'status'      => 'STORED_AT_HUB',
            'updated_at'  => now()
        ]);

        return response()->json([
            'success'     => true,
            'message'     => 'Người bán check-in thành công!',
            'locker_code' => $emptyLocker->locker_code,
            'instruction' => "Vui lòng dán tem mã đơn {$order->order_code} và xếp vào {$emptyLocker->locker_code}."
        ]);
    }

    /**
     * Nhân viên Trạm Hub quét mã CHECK-OUT (Người mua đến nhận đồ)
     */
    public function processCheckout(Request $request)
    {
        $validated = $request->validate([
            'order_code' => 'required|string',
            'token'      => 'required|string',
            'buyer_id'   => 'required|integer'
        ]);

        $isValid = $this->qrEngine->verifyToken($validated['order_code'], $validated['buyer_id'], 'BUYER', $validated['token']);
        if (!$isValid) {
            return response()->json(['success' => false, 'message' => 'Mã QR đã hết hạn hoặc không hợp lệ.'], 400);
        }

        $order = DB::table('escrow_orders')->where('order_code', $validated['order_code'])->first();
        if (!$order || $order->status !== 'STORED_AT_HUB') {
            return response()->json(['success' => false, 'message' => 'Đơn hàng không ở trạng thái sẵn sàng để lấy đồ.'], 400);
        }

        // Mở khóa ô tủ
        if ($order->locker_id) {
            DB::table('lockers')->where('id', $order->locker_id)->update([
                'status'           => 'EMPTY',
                'current_order_id' => null
            ]);
        }

        DB::table('escrow_orders')->where('id', $order->id)->update([
            'status'     => 'INSPECTING_AT_HUB',
            'updated_at' => now()
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Xác nhận mã nhận hàng thành công! Đã mở ô tủ để sinh viên kiểm tra hàng tại Trạm Hub.'
        ]);
    }
}
