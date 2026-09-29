-- ====================================================================
-- HUNRE AUTH SERVICE - DATABASE INITIALIZATION SCRIPT
-- Schema Version: 3.0 (Auth-Only, Token-Based Authentication)
-- University: Hanoi University of Natural Resources and Environment
-- ====================================================================

CREATE DATABASE IF NOT EXISTS `hunre_ecommerce` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `hunre_ecommerce`;

-- ====================================================================
-- 1. USERS & STUDENT PROFILES
-- ====================================================================
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
    `wallet_balance` DECIMAL(15,2) DEFAULT 0.00,
    `escrow_locked_balance` DECIMAL(15,2) DEFAULT 0.00,
    `avatar_url` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ====================================================================
-- 2. API TOKENS (Bearer Token Authentication)
-- Mỗi lần đăng nhập tạo 1 token mới, lưu hash vào đây.
-- Middleware CheckBearerToken sẽ tra cứu bảng này để xác thực.
-- ====================================================================
CREATE TABLE IF NOT EXISTS `api_tokens` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `user_id` BIGINT UNSIGNED NOT NULL,
    `token_hash` VARCHAR(64) UNIQUE NOT NULL COMMENT 'SHA-256 hash của raw token',
    `token_prefix` VARCHAR(12) NOT NULL COMMENT '12 ký tự đầu của raw token (để log/debug)',
    `expires_at` TIMESTAMP NOT NULL COMMENT 'Token hết hạn sau 24 giờ',
    `last_used_at` TIMESTAMP NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
    INDEX `idx_token_hash` (`token_hash`),
    INDEX `idx_user_id` (`user_id`)
) ENGINE=InnoDB;

-- ====================================================================
-- SEED DATA MẪU (SINH VIÊN HUNRE)
-- Password mặc định cho tất cả: "password123"
-- Hash: $2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi
-- ====================================================================
INSERT INTO `users` (`id`, `student_code`, `full_name`, `email`, `password_hash`, `phone`, `campus`, `faculty`, `trust_score`, `role`, `wallet_balance`) VALUES
(1, '20211001', 'Nguyễn Văn An',       'an.nv@hunre.edu.vn',     '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0981112233', 'CS1_HA_NOI', 'Công nghệ Thông tin', 520, 'STUDENT',   500000.00),
(2, '20211002', 'Trần Thị Bích',       'bich.tt@hunre.edu.vn',   '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0982223344', 'CS1_HA_NOI', 'Quản lý Đất đai',    480, 'STUDENT',   250000.00),
(3, '20211003', 'Lê Hoàng Cường',      'cuong.lh@hunre.edu.vn',  '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0983334455', 'CS1_HA_NOI', 'Môi trường',         390, 'STUDENT',   120000.00),
(4, 'HUB001',   'Cộng Tác Viên Hub',   'hub.cs1@hunre.edu.vn',   '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0989998877', 'CS1_HA_NOI', 'Văn Phòng Đoàn',     999, 'HUB_STAFF', 0.00),
(5, 'ADMIN001',  'Quản Trị Viên HUNRE', 'admin@hunre.edu.vn',     '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', '0900000001', 'CS1_HA_NOI', 'Ban Giám Hiệu',      999, 'ADMIN',     0.00);
