-- ====================================================================
-- HUNRE E-COMMERCE DATABASE INITIALIZATION SCRIPT
-- Schema Version: 2.0 (Enterprise Microservices & Double-Entry Escrow)
-- University: Hanoi University of Natural Resources and Environment
-- ====================================================================

CREATE DATABASE IF NOT EXISTS `hunre_ecommerce` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `hunre_ecommerce`;

-- 1. USERS & STUDENT PROFILES
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_code` VARCHAR(30) UNIQUE NOT NULL COMMENT 'Mã sinh viên HUNRE, ví dụ: 20211005',
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) UNIQUE NOT NULL COMMENT 'Email định danh trường @hunre.edu.vn',
    `password_hash` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(20) NULL,
    `campus` ENUM('CS1_HA_NOI', 'CS2_THANH_HOA') DEFAULT 'CS1_HA_NOI',
    `faculty` VARCHAR(100) DEFAULT 'Công nghệ Thông tin',
    `trust_score` INT DEFAULT 100 COMMENT 'Điểm uy tín sinh viên (Thang 0 - 1000)',
    `kyc_status` ENUM('UNVERIFIED', 'PENDING', 'VERIFIED') DEFAULT 'VERIFIED',
    `role` ENUM('STUDENT', 'HUB_STAFF', 'ADMIN') DEFAULT 'STUDENT',
    `wallet_balance` DECIMAL(15,2) DEFAULT 0.00 COMMENT 'Số dư ví khả dụng',
    `escrow_locked_balance` DECIMAL(15,2) DEFAULT 0.00 COMMENT 'Số dư tiền đang bị đóng băng ký quỹ',
    `avatar_url` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. CATEGORIES
CREATE TABLE IF NOT EXISTS `categories` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `slug` VARCHAR(100) UNIQUE NOT NULL,
    `icon` VARCHAR(50) DEFAULT 'fa-box',
    `description` TEXT NULL
) ENGINE=InnoDB;

-- 3. PRODUCTS & CATALOG
CREATE TABLE IF NOT EXISTS `products` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `seller_id` BIGINT UNSIGNED NOT NULL,
    `category_id` INT UNSIGNED NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT NOT NULL,
    `original_price` DECIMAL(15,2) NOT NULL COMMENT 'Giá bán đề xuất',
    `current_price` DECIMAL(15,2) NOT NULL COMMENT 'Giá hiện tại (sau giảm giá time-decay)',
    `floor_price` DECIMAL(15,2) NOT NULL COMMENT 'Giá sàn tối thiểu chấp nhận',
    `is_time_decay` TINYINT(1) DEFAULT 0 COMMENT 'Bật chế độ tự động hạ giá theo thời gian',
    `decay_rate_per_hour` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Số tiền giảm mỗi giờ',
    `condition_grade` ENUM('GRADE_S', 'GRADE_A', 'GRADE_B', 'GRADE_C') DEFAULT 'GRADE_A' COMMENT 'Phân loại chất lượng AI',
    `ai_defect_score` FLOAT DEFAULT 0.0 COMMENT 'Tỷ lệ lỗi/trầy xước quét bởi AI (0.0 - 1.0)',
    `ai_inspection_summary` VARCHAR(255) NULL COMMENT 'Bản tóm tắt kết quả kiểm định AI',
    `is_barter_eligible` TINYINT(1) DEFAULT 1 COMMENT 'Cho phép ghép cặp trao đổi đồ (AI Barter Graph)',
    `desired_exchange_items` VARCHAR(255) NULL COMMENT 'Món đồ mong muốn đổi lấy, ví dụ: Giáo trình CSDL, Bàn phím',
    `status` ENUM('ACTIVE', 'RESERVED_FOR_HUB', 'STORED_IN_HUB', 'SOLD', 'CANCELLED') DEFAULT 'ACTIVE',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`seller_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`category_id`) REFERENCES `categories`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- 4. PRODUCT IMAGES & ANTI-FRAUD HASHES
CREATE TABLE IF NOT EXISTS `product_images` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `product_id` BIGINT UNSIGNED NOT NULL,
    `image_url` VARCHAR(255) NOT NULL,
    `is_primary` TINYINT(1) DEFAULT 0,
    `phash_code` VARCHAR(64) NULL COMMENT 'Mã băm cảm nhận thị giác pHash chống ảnh mạng',
    `is_ai_verified` TINYINT(1) DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 5. PHYSICAL HUBS & SMART LOCKERS
CREATE TABLE IF NOT EXISTS `hubs` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(150) NOT NULL,
    `campus` ENUM('CS1_HA_NOI', 'CS2_THANH_HOA') NOT NULL,
    `location_detail` VARCHAR(255) NOT NULL COMMENT 'Ví dụ: Phòng Đoàn Thanh Niên - Tầng 1 Nhà A',
    `staff_in_charge` VARCHAR(100) NOT NULL,
    `contact_phone` VARCHAR(20) NOT NULL,
    `operating_hours` VARCHAR(100) DEFAULT '08:00 - 17:30 (Thứ 2 - Thứ 7)'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `lockers` (
    `id` INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `hub_id` INT UNSIGNED NOT NULL,
    `locker_code` VARCHAR(50) NOT NULL COMMENT 'Ví dụ: CS1-A-01',
    `size_type` ENUM('SMALL', 'MEDIUM', 'LARGE') DEFAULT 'MEDIUM',
    `status` ENUM('EMPTY', 'OCCUPIED', 'MAINTENANCE') DEFAULT 'EMPTY',
    `current_order_id` BIGINT UNSIGNED NULL,
    FOREIGN KEY (`hub_id`) REFERENCES `hubs`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 6. SMART ESCROW ORDERS & STATE MACHINE
CREATE TABLE IF NOT EXISTS `escrow_orders` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `order_code` VARCHAR(50) UNIQUE NOT NULL COMMENT 'Ví dụ: ORD-HUNRE-98471',
    `buyer_id` BIGINT UNSIGNED NOT NULL,
    `seller_id` BIGINT UNSIGNED NOT NULL,
    `product_id` BIGINT UNSIGNED NOT NULL,
    `hub_id` INT UNSIGNED NOT NULL,
    `locker_id` INT UNSIGNED NULL,
    `order_type` ENUM('DIRECT_BUY', 'BARTER_SWAP') DEFAULT 'DIRECT_BUY',
    `escrow_amount` DECIMAL(15,2) NOT NULL COMMENT 'Số tiền ký quỹ',
    `status` ENUM('INITIATED', 'ESCROW_LOCKED', 'STORED_AT_HUB', 'INSPECTING_AT_HUB', 'RELEASED', 'DISPUTED', 'REFUNDED') DEFAULT 'INITIATED',
    `seller_checkin_qr` VARCHAR(255) NULL COMMENT 'Mã HMAC QR người bán gửi đồ',
    `buyer_checkout_qr` VARCHAR(255) NULL COMMENT 'Mã HMAC QR người mua nhận đồ',
    `deposit_deadline` TIMESTAMP NULL,
    `hub_pickup_deadline` TIMESTAMP NULL,
    `completed_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`buyer_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`seller_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`),
    FOREIGN KEY (`hub_id`) REFERENCES `hubs`(`id`)
) ENGINE=InnoDB;

-- 7. DOUBLE-ENTRY ESCROW LEDGER (SỔ CÁI KẾ TOÁN KÉP)
CREATE TABLE IF NOT EXISTS `escrow_ledger` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `order_id` BIGINT UNSIGNED NOT NULL,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `transaction_type` ENUM('HOLD_DEPOSIT', 'RELEASE_TO_SELLER', 'REFUND_TO_BUYER', 'PENALTY_DEDUCT') NOT NULL,
    `amount` DECIMAL(15,2) NOT NULL,
    `balance_after` DECIMAL(15,2) NOT NULL,
    `idempotency_key` VARCHAR(64) UNIQUE NOT NULL,
    `note` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`order_id`) REFERENCES `escrow_orders`(`id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB;

-- 8. BARTER CYCLES (VÒNG TRÒN TRAO ĐỔI ĐỒ AI)
CREATE TABLE IF NOT EXISTS `barter_cycles` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `cycle_code` VARCHAR(50) UNIQUE NOT NULL,
    `cycle_length` INT DEFAULT 3 COMMENT '2-way, 3-way hoặc 4-way swap',
    `status` ENUM('PROPOSED', 'ALL_ACCEPTED', 'IN_TRANSIT_HUB', 'COMPLETED', 'BROKEN') DEFAULT 'PROPOSED',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `barter_cycle_nodes` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `cycle_id` BIGINT UNSIGNED NOT NULL,
    `giver_user_id` BIGINT UNSIGNED NOT NULL,
    `receiver_user_id` BIGINT UNSIGNED NOT NULL,
    `product_id` BIGINT UNSIGNED NOT NULL,
    `cash_compensation` DECIMAL(15,2) DEFAULT 0.00 COMMENT 'Khoản bù trừ tiền mặt (+ nhận thêm, - nạp bù)',
    `has_accepted` TINYINT(1) DEFAULT 0,
    FOREIGN KEY (`cycle_id`) REFERENCES `barter_cycles`(`id`) ON DELETE CASCADE,
    FOREIGN KEY (`giver_user_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`receiver_user_id`) REFERENCES `users`(`id`),
    FOREIGN KEY (`product_id`) REFERENCES `products`(`id`)
) ENGINE=InnoDB;

-- 9. DISPUTES & ARBITRATION
CREATE TABLE IF NOT EXISTS `disputes` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `order_id` BIGINT UNSIGNED NOT NULL,
    `raised_by_id` BIGINT UNSIGNED NOT NULL,
    `reason` TEXT NOT NULL,
    `evidence_photo_url` VARCHAR(255) NULL,
    `hub_staff_note` TEXT NULL,
    `resolution` ENUM('PENDING', 'BUYER_FULL_REFUND', 'SELLER_RELEASE', 'PARTIAL_SPLIT') DEFAULT 'PENDING',
    `resolved_at` TIMESTAMP NULL,
    FOREIGN KEY (`order_id`) REFERENCES `escrow_orders`(`id`),
    FOREIGN KEY (`raised_by_id`) REFERENCES `users`(`id`)
) ENGINE=InnoDB;

-- ====================================================================
-- SEED DATA MẪU (DỮ LIỆU THỰC TẾ SINH VIÊN HUNRE)
-- ====================================================================

-- Thêm tài khoản mẫu
INSERT INTO `users` (`id`, `student_code`, `full_name`, `email`, `password_hash`, `phone`, `campus`, `faculty`, `trust_score`, `role`, `wallet_balance`) VALUES
(1, '20211001', 'Nguyễn Văn An', 'an.nv@hunre.edu.vn', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0981112233', 'CS1_HA_NOI', 'Công nghệ Thông tin', 520, 'STUDENT', 500000.00),
(2, '20211002', 'Trần Thị Bích', 'bich.tt@hunre.edu.vn', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0982223344', 'CS1_HA_NOI', 'Quản lý Đất đai', 480, 'STUDENT', 250000.00),
(3, '20211003', 'Lê Hoàng Cường', 'cuong.lh@hunre.edu.vn', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0983334455', 'CS1_HA_NOI', 'Môi trường', 390, 'STUDENT', 120000.00),
(4, 'HUB001', 'Cộng Tác Viên Trạm Hub', 'hub.cs1@hunre.edu.vn', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0989998877', 'CS1_HA_NOI', 'Văn Phòng Đoàn Trường', 999, 'HUB_STAFF', 0.00);

-- Danh mục
INSERT INTO `categories` (`id`, `name`, `slug`, `icon`, `description`) VALUES
(1, 'Giáo Trình & Tài Liệu', 'giao-trinh', 'fa-book-open', 'Sách giáo trình các khoa Môi trường, Trắc địa, CNTT, Đất đai'),
(2, 'Thiết Bị Điện Tử & Laptop', 'thiet-bi-dien-tu', 'fa-laptop', 'Laptop, màn hình máy tính, chuột phím cơ, máy tính cầm tay Casio'),
(3, 'Dụng Cụ Học Tập & Đồ Dùng', 'dung-cu-hoc-tap', 'fa-ruler-combined', 'Thước vẽ kỹ thuật, bảng vẽ đồ họa, đèn bàn LED sinh viên');

-- Trạm Hub HUNRE
INSERT INTO `hubs` (`id`, `name`, `campus`, `location_detail`, `staff_in_charge`, `contact_phone`) VALUES
(1, 'Trạm Hub Trung Gian CS1', 'CS1_HA_NOI', 'Văn phòng Hội Sinh Viên - Tầng 1 Nhà A (41A Phú Diễn, Bắc Từ Liêm, HN)', 'Đoàn Thanh Niên HUNRE', '02438370598'),
(2, 'Trạm Hub Trung Gian CS2', 'CS2_THANH_HOA', 'Văn phòng Quản lý Đào tạo - Cơ sở Bỉm Sơn, Thanh Hóa', 'Phụ Trách Hub CS2', '02373824125');

-- Ô tủ Locker tại Trạm CS1
INSERT INTO `lockers` (`id`, `hub_id`, `locker_code`, `size_type`, `status`) VALUES
(1, 1, 'LOCKER-S-01', 'SMALL', 'EMPTY'),
(2, 1, 'LOCKER-M-01', 'MEDIUM', 'EMPTY'),
(3, 1, 'LOCKER-M-02', 'MEDIUM', 'EMPTY'),
(4, 1, 'LOCKER-L-01', 'LARGE', 'EMPTY');

-- Sản phẩm mẫu cho chu trình Barter Graph 3 chiều
INSERT INTO `products` (`id`, `seller_id`, `category_id`, `title`, `description`, `original_price`, `current_price`, `floor_price`, `is_time_decay`, `condition_grade`, `ai_inspection_summary`, `is_barter_eligible`, `desired_exchange_items`, `status`) VALUES
(1, 1, 1, 'Giáo trình Cơ Sở Dữ Liệu & SQL (HUNRE)', 'Sách bảo quản tốt, không quăn mép, có ghi chú bút chì vài bài tập', 80000.00, 75000.00, 60000.00, 1, 'GRADE_A', 'Độ mới 94%, không rách, mép trang sạch', 1, 'Máy tính Casio FX 580VN', 'ACTIVE'),
(2, 2, 2, 'Máy tính Casio FX 580VN X', 'Dùng tốt cho môn Toán cao cấp và Khí tượng, nguyên tem bảo hành', 350000.00, 320000.00, 280000.00, 0, 'GRADE_S', 'Độ mới 98%, màn hình LCD sắc nét, phím nảy nhạy', 1, 'Bàn phím cơ DareU hoặc Balo', 'ACTIVE'),
(3, 3, 2, 'Bàn phím cơ DareU EK87 Blue Switch', 'Phím gõ nảy tốt, led trắng đơn sắc, dọn trọ cần đổi giáo trình', 280000.00, 250000.00, 200000.00, 1, 'GRADE_B', 'Độ mới 88%, hơi xước góc trái, các switch hoạt động 100%', 1, 'Giáo trình CSDL hoặc Sách Tiếng Anh', 'ACTIVE');
