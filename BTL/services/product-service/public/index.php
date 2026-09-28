<?php
/**
 * HUNRE E-COMMERCE - PRODUCT CATALOG & POSTING SERVICE
 * Microservice: Quản lý đăng bán, thêm, sửa, xóa (CRUD) & hạ giá tự động
 * Port: 8002
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Đường dẫn file lưu trữ dữ liệu sản phẩm (tự tạo nếu chưa có)
$dataFile = sys_get_temp_dir() . '/hunre_products.json';

// Dữ liệu ban đầu mặc định
$defaultProducts = [
    [
        "id" => 1,
        "seller_id" => 1,
        "seller_name" => "Nguyễn Văn An",
        "category_name" => "Giáo Trình & Tài Liệu",
        "category_id" => "BOOKS",
        "title" => "Giáo trình Cơ Sở Dữ Liệu & SQL (HUNRE)",
        "description" => "Giáo trình dùng cho sinh viên K11, K12 CNTT. Trang sạch, không quăn mép.",
        "current_price" => 75000.0,
        "original_price" => 80000.0,
        "floor_price" => 60000.0,
        "condition_grade" => "GRADE_A",
        "ai_inspection_summary" => "Độ mới 94%, không rách, mép trang sạch",
        "is_barter_eligible" => 1,
        "desired_exchange_items" => "Máy tính Casio FX 580VN",
        "image_url" => "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop",
        "status" => "ACTIVE",
        "created_at" => "2026-09-15 08:30:00"
    ],
    [
        "id" => 2,
        "seller_id" => 2,
        "seller_name" => "Trần Thị Bích",
        "category_name" => "Dụng Cụ Học Tập",
        "category_id" => "TECH",
        "title" => "Máy tính Casio FX 580VN X (Like New)",
        "description" => "Máy tính chính hãng thi tốt nghiệp và đại học, nguyên tem Bộ GD&ĐT.",
        "current_price" => 320000.0,
        "original_price" => 350000.0,
        "floor_price" => 280000.0,
        "condition_grade" => "GRADE_S",
        "ai_inspection_summary" => "Độ mới 98%, màn hình LCD sắc nét, phím nảy nhạy",
        "is_barter_eligible" => 1,
        "desired_exchange_items" => "Bàn phím cơ DareU hoặc Balo",
        "image_url" => "https://images.unsplash.com/photo-1596495578065-6e0763fa1178?w=600&auto=format&fit=crop",
        "status" => "ACTIVE",
        "created_at" => "2026-09-15 09:15:00"
    ],
    [
        "id" => 3,
        "seller_id" => 3,
        "seller_name" => "Lê Hoàng Cường",
        "category_name" => "Thiết Bị Điện Tử",
        "category_id" => "TECH",
        "title" => "Bàn phím cơ DareU EK87 Blue Switch",
        "description" => "Bàn phím cơ dây cắm Type-C, switch nhận 100%, gõ êm mượt.",
        "current_price" => 250000.0,
        "original_price" => 280000.0,
        "floor_price" => 200000.0,
        "condition_grade" => "GRADE_B",
        "ai_inspection_summary" => "Độ mới 88%, hơi xước góc trái, các switch hoạt động 100%",
        "is_barter_eligible" => 1,
        "desired_exchange_items" => "Giáo trình CSDL hoặc Sách Tiếng Anh",
        "image_url" => "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop",
        "status" => "ACTIVE",
        "created_at" => "2026-09-15 10:00:00"
    ]
];

// Nạp dữ liệu
if (!file_exists($dataFile)) {
    file_put_contents($dataFile, json_encode($defaultProducts, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$products = json_decode(file_get_contents($dataFile), true) ?: $defaultProducts;

// Phân tích URL & Method
$method = $_SERVER['REQUEST_METHOD'];
$uri = $_SERVER['REQUEST_URI'];
$path = parse_url($uri, PHP_URL_PATH);

// Tách ID từ URL nếu có (ví dụ: /api/v1/products/1 hoặc /1)
$pathParts = explode('/', trim($path, '/'));
$productId = null;
$lastSegment = end($pathParts);
if (is_numeric($lastSegment)) {
    $productId = (int)$lastSegment;
} elseif (isset($_GET['id']) && is_numeric($_GET['id'])) {
    $productId = (int)$_GET['id'];
}

// -------------------------------------------------------------
// 1. GET: XEM DANH SÁCH HOẶC CHI TIẾT SẢN PHẨM
// -------------------------------------------------------------
if ($method === 'GET') {
    if ($productId !== null) {
        foreach ($products as $p) {
            if ($p['id'] === $productId) {
                echo json_encode(['success' => true, 'data' => $p]);
                exit;
            }
        }
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => "Không tìm thấy sản phẩm #{$productId}."]);
        exit;
    }

    // Lọc theo danh mục nếu có
    $category = $_GET['category'] ?? null;
    $filtered = array_values(array_filter($products, function($item) use ($category) {
        if ($category && $category !== 'ALL' && ($item['category_id'] ?? '') !== $category) {
            return false;
        }
        return ($item['status'] ?? 'ACTIVE') !== 'DELETED';
    }));

    echo json_encode([
        'success' => true,
        'count' => count($filtered),
        'data' => $filtered
    ]);
    exit;
}

// Đọc payload JSON gửi lên
$input = json_decode(file_get_contents('php://input'), true) ?: $_POST;

// -------------------------------------------------------------
// 2. POST: ĐĂNG BÁN SẢN PHẨM MỚI (THÊM MỚI)
// -------------------------------------------------------------
if ($method === 'POST' && ($productId === null || strpos($path, 'create') !== false)) {
    $title = trim($input['title'] ?? '');
    if (empty($title)) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Tiêu đề sản phẩm không được để trống!']);
        exit;
    }

    $newId = count($products) > 0 ? max(array_column($products, 'id')) + 1 : 1;
    $originalPrice = (float)($input['original_price'] ?? $input['price'] ?? 50000);
    $floorPrice = (float)($input['floor_price'] ?? ($originalPrice * 0.8));

    $newProduct = [
        "id" => $newId,
        "seller_id" => (int)($input['seller_id'] ?? 1),
        "seller_name" => $input['seller_name'] ?? "Nguyễn Văn An",
        "category_name" => $input['category_name'] ?? ($input['category_id'] === 'BOOKS' ? 'Giáo Trình & Tài Liệu' : 'Thiết Bị Điện Tử'),
        "category_id" => $input['category_id'] ?? 'BOOKS',
        "title" => $title,
        "description" => $input['description'] ?? 'Sản phẩm sinh viên HUNRE đăng bán.',
        "current_price" => $originalPrice,
        "original_price" => $originalPrice,
        "floor_price" => $floorPrice,
        "condition_grade" => $input['condition_grade'] ?? 'GRADE_A',
        "ai_inspection_summary" => $input['ai_inspection_summary'] ?? 'Đã qua thẩm định thị giác AI HUNRE',
        "is_barter_eligible" => isset($input['is_barter_eligible']) ? (int)$input['is_barter_eligible'] : 1,
        "desired_exchange_items" => $input['desired_exchange_items'] ?? 'Máy tính hoặc sách chuyên ngành',
        "image_url" => $input['image_url'] ?? 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&auto=format&fit=crop',
        "status" => "ACTIVE",
        "created_at" => date('Y-m-d H:i:s')
    ];

    $products[] = $newProduct;
    file_put_contents($dataFile, json_encode($products, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    http_response_code(201);
    echo json_encode([
        'success' => true,
        'message' => 'Đăng bán sản phẩm thành công lên sàn HUNRE!',
        'product' => $newProduct
    ]);
    exit;
}

// -------------------------------------------------------------
// 3. PUT / PATCH: CHỈNH SỬA THÔNG TIN SẢN PHẨM (SỬA)
// -------------------------------------------------------------
if ($method === 'PUT' || ($method === 'POST' && strpos($path, 'update') !== false)) {
    $targetId = $productId ?? (int)($input['id'] ?? 0);
    $found = false;

    foreach ($products as &$p) {
        if ($p['id'] === $targetId) {
            if (isset($input['title'])) $p['title'] = trim($input['title']);
            if (isset($input['description'])) $p['description'] = trim($input['description']);
            if (isset($input['current_price'])) $p['current_price'] = (float)$input['current_price'];
            if (isset($input['floor_price'])) $p['floor_price'] = (float)$input['floor_price'];
            if (isset($input['desired_exchange_items'])) $p['desired_exchange_items'] = trim($input['desired_exchange_items']);
            if (isset($input['category_id'])) $p['category_id'] = $input['category_id'];
            if (isset($input['condition_grade'])) $p['condition_grade'] = $input['condition_grade'];
            $p['updated_at'] = date('Y-m-d H:i:s');
            $found = true;
            break;
        }
    }

    if (!$found) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => "Không tìm thấy sản phẩm #{$targetId} để chỉnh sửa."]);
        exit;
    }

    file_put_contents($dataFile, json_encode($products, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode([
        'success' => true,
        'message' => "Cập nhật thông tin sản phẩm #{$targetId} thành công!"
    ]);
    exit;
}

// -------------------------------------------------------------
// 4. DELETE: XÓA HOẶC GỠ SẢN PHẨM KHỎI SÀN (XÓA)
// -------------------------------------------------------------
if ($method === 'DELETE' || ($method === 'POST' && strpos($path, 'delete') !== false)) {
    $targetId = $productId ?? (int)($input['id'] ?? 0);
    $initialCount = count($products);

    $products = array_values(array_filter($products, function($p) use ($targetId) {
        return $p['id'] !== $targetId;
    }));

    if (count($products) === $initialCount) {
        http_response_code(404);
        echo json_encode(['success' => false, 'message' => "Không tìm thấy sản phẩm #{$targetId} để xóa."]);
        exit;
    }

    file_put_contents($dataFile, json_encode($products, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    echo json_encode([
        'success' => true,
        'message' => "Đã xóa sản phẩm #{$targetId} khỏi sàn giao dịch HUNRE."
    ]);
    exit;
}

http_response_code(405);
echo json_encode(['success' => false, 'message' => 'Phương thức HTTP không được hỗ trợ.']);
