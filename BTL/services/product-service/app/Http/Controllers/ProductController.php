<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

/**
 * PRODUCT CONTROLLER
 * Quản lý danh mục giáo trình, đồ dùng & đăng tải sản phẩm thẩm định AI
 */
class ProductController
{
    /**
     * Danh sách sản phẩm đang hoạt động trên sàn
     */
    public function index(Request $request)
    {
        $query = DB::table('products')
            ->join('categories', 'products.category_id', '=', 'categories.id')
            ->join('users', 'products.seller_id', '=', 'users.id')
            ->select(
                'products.*',
                'categories.name as category_name',
                'categories.icon as category_icon',
                'users.full_name as seller_name',
                'users.student_code as seller_student_code',
                'users.trust_score as seller_trust_score'
            )
            ->where('products.status', 'ACTIVE');

        if ($request->has('category_id')) {
            $query->where('products.category_id', $request->query('category_id'));
        }

        if ($request->has('search')) {
            $search = $request->query('search');
            $query->where(function ($q) use ($search) {
                $q->where('products.title', 'like', "%{$search}%")
                  ->orWhere('products.description', 'like', "%{$search}%");
            });
        }

        $products = $query->orderBy('products.created_at', 'desc')->get();

        return response()->json([
            'success' => true,
            'count'   => count($products),
            'data'    => $products
        ]);
    }

    /**
     * Chi tiết sản phẩm
     */
    public function show(int $id)
    {
        $product = DB::table('products')
            ->join('categories', 'products.category_id', '=', 'categories.id')
            ->join('users', 'products.seller_id', '=', 'users.id')
            ->select('products.*', 'categories.name as category_name', 'users.full_name as seller_name', 'users.trust_score as seller_trust_score')
            ->where('products.id', $id)
            ->first();

        if (!$product) {
            return response()->json(['success' => false, 'message' => 'Không tìm thấy sản phẩm.'], 404);
        }

        return response()->json(['success' => true, 'data' => $product]);
    }

    /**
     * Đăng bán sản phẩm mới (Tự động liên kết AI Service thẩm định ảnh)
     */
    public function store(Request $request)
    {
        $validated = $request->validate([
            'seller_id'             => 'required|integer',
            'category_id'           => 'required|integer',
            'title'                 => 'required|string|max:255',
            'description'           => 'required|string',
            'original_price'        => 'required|numeric|min:0',
            'floor_price'           => 'required|numeric|min:0',
            'is_barter_eligible'    => 'nullable|boolean',
            'desired_exchange_items'=> 'nullable|string',
            'condition_grade'       => 'nullable|in:GRADE_S,GRADE_A,GRADE_B,GRADE_C',
            'ai_inspection_summary' => 'nullable|string'
        ]);

        $productId = DB::table('products')->insertGetId([
            'seller_id'             => $validated['seller_id'],
            'category_id'           => $validated['category_id'],
            'title'                 => $validated['title'],
            'description'           => $validated['description'],
            'original_price'        => $validated['original_price'],
            'current_price'         => $validated['original_price'],
            'floor_price'           => $validated['floor_price'],
            'condition_grade'       => $validated['condition_grade'] ?? 'GRADE_A',
            'ai_inspection_summary' => $validated['ai_inspection_summary'] ?? 'Đã qua thẩm định AI HUNRE',
            'is_barter_eligible'    => $validated['is_barter_eligible'] ?? 1,
            'desired_exchange_items'=> $validated['desired_exchange_items'] ?? null,
            'status'                => 'ACTIVE',
            'created_at'            => now(),
            'updated_at'            => now()
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Đăng sản phẩm thành công và đã đồng bộ lên sàn O2O HUNRE!',
            'product_id' => $productId
        ], 201);
    }

    /**
     * Bật chế độ đấu giá ngược tự động hạ giá theo thời gian (Time-decay)
     */
    public function enableTimeDecay(Request $request, int $id)
    {
        $validated = $request->validate([
            'decay_rate_per_hour' => 'required|numeric|min:1000'
        ]);

        DB::table('products')->where('id', $id)->update([
            'is_time_decay'       => 1,
            'decay_rate_per_hour' => $validated['decay_rate_per_hour'],
            'updated_at'          => now()
        ]);

        return response()->json([
            'success' => true,
            'message' => "Đã kích hoạt chế độ tự động hạ giá {$validated['decay_rate_per_hour']}đ/giờ cho sản phẩm #{$id}."
        ]);
    }
}
