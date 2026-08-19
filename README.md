# Course Registration System (CRS) - Microservices Architecture

**Người thực hiện:** Nguyễn Văn Chiến  

Hệ thống đăng ký môn học CRS (Course Registration System) là một ứng dụng Fullstack được xây dựng hoàn toàn dựa trên kiến trúc Microservices hiện đại, kết hợp với giao diện Frontend ReactJS. 

Dự án cung cấp luồng quy trình khép kín từ xác thực người dùng tập trung, định tuyến bảo mật cho tới giao tiếp liên dịch vụ (Inter-service Communication).

---

## 🚀 Cấu trúc hệ thống & Chức năng chính (Features)

Dự án bao gồm 5 module chính (4 Backend Services + 1 Frontend):

### 1. 🛡️ API Gateway (`api-gateway` - Cổng 8080)
- **Định tuyến (Routing)**: Chịu trách nhiệm làm "cửa ngõ" duy nhất, nhận mọi luồng request từ Frontend/Client và định tuyến (RewritePath) tới chính xác các service bên trong.
- **Bảo mật & CORS**: Cấu hình Global CORS cấp quyền truy cập cho Frontend (`http://localhost:5173`).
- **Global Filters**:
  - `AuthHeaderFilter`: Kiểm tra chặn bắt buộc phải có `Authorization: Bearer` trước khi cho phép đi sâu vào các service nghiệp vụ (trừ các public routes).
  - `ApiKeyFilter`: Xác thực API Key (`X-API-KEY`) dành riêng cho các đối tác thứ ba khi gọi các public endpoint.

### 2. 🔐 Authentication Service (`auth-service` - Cổng 8081)
- **Quản lý tài khoản**: Chứa bảng `app_user` lưu trữ thông tin đăng nhập và Role (`ADMIN`, `STUDENT`) với mật khẩu mã hóa an toàn bằng BCrypt.
- **Cấp phát JWT**: Sử dụng thư viện `JJWT 0.12.6` thế hệ mới nhất để mã hóa và cấp phát Token an toàn.
- **Data Seeder tự động**: Tự động sinh sẵn tài khoản mẫu để test hệ thống (`admin/admin123`, `student1/student123`).

### 3. 📚 Course Service (`course-service` - Cổng 8082)
- **Quản lý Môn học (CRUD)**: Đầy đủ các tác vụ lấy danh sách, thêm, sửa, xóa môn học.
- **Inter-service API**: Cung cấp endpoint nội bộ (`/internal/courses/`) để `registration-service` gọi sang trừ số chỗ, trả lại chỗ.
- **Bảo vệ bằng Spring Security**: Cấu hình Role-based Access Control (RBAC). Các thao tác thêm, sửa, xóa bắt buộc phải là quyền `ADMIN`.

### 4. 📝 Registration Service (`registration-service` - Cổng 8083)
- **Nghiệp vụ Đăng ký**: Sinh viên đăng ký hoặc hủy đăng ký lớp học. Hệ thống tự động kiểm tra xem sinh viên đã đăng ký môn đó chưa.
- **Giao tiếp liên dịch vụ (Inter-Service)**: Sử dụng `RestTemplate` (đã nâng cấp với `httpclient5` để hỗ trợ method `PATCH`) để gọi sang `course-service` nhằm cập nhật số lượng chỗ ngồi (còn lại) theo thời gian thực một cách an toàn.
- **Xử lý lỗi (Global Exception Handling)**: Bắt lỗi 400 Bad Request, 404 Not Found, 409 Conflict trả về mã lỗi JSON đồng bộ, đẹp mắt.

### 5. 💻 Frontend App (`crs-frontend` - Cổng 5173)
- **Công nghệ**: ReactJS + TypeScript + Vite. Cấu trúc thư mục chuyên nghiệp (`api`, `components`, `types`, `pages`, `context`).
- **Axios Configuration**: Tích hợp biến môi trường (`.env`) và định tuyến toàn bộ API calls qua 1 endpoint duy nhất của Gateway (`http://localhost:8080/api`).
- **An toàn kiểu dữ liệu (Type-Safety)**: Map chuẩn xác hoàn toàn 1:1 các Interface (Course, LoginRequest, Registration...) với các DTO của Backend.

---

## 🛠️ Hướng dẫn khởi chạy

### Yêu cầu môi trường
- Java 17+ (JDK)
- Node.js & npm (Phiên bản mới nhất)
- MySQL Server đang chạy (port `3306`), tạo sẵn password là `123456` (Cấu hình thay đổi trong file `application.properties` của từng service).

### Bước 1: Khởi động hệ thống Backend
Mở Terminal ở thư mục gốc của project và chạy lần lượt 4 service:
```bash
# Gateway (Chạy đầu tiên hoặc cuối cùng đều được)
cd api-gateway && ./mvnw spring-boot:run

# Auth Service
cd auth-service && ./mvnw spring-boot:run

# Course Service
cd course-service && ./mvnw spring-boot:run

# Registration Service
cd registration-service && ./mvnw spring-boot:run
```

### Bước 2: Khởi động Frontend
Mở một cửa sổ Terminal mới:
```bash
cd crs-frontend
npm install
npm run dev
```

Sau khi chạy xong, truy cập **[http://localhost:5173](http://localhost:5173)** trên trình duyệt để kiểm tra kết nối hệ thống!

---

## 🧪 Kịch bản Test (Postman)

Để phục vụ báo cáo, hệ thống có cung cấp sẵn các Test Case thông qua Postman:

1. **Test Lấy Token**: Gọi `POST http://localhost:8080/api/auth/login` với body `{"username": "student1", "password": "student123"}` -> Lấy Token.
2. **Test Xem danh sách môn**: Gọi `GET http://localhost:8080/api/courses` qua Gateway (Truyền Token vào Authorization).
3. **Test Quyền ADMIN**: Lấy Token của Admin (`admin/admin123`) và test gọi `POST http://localhost:8080/api/courses` để tạo môn.
4. **Test Đăng ký học (Inter-service)**: Gọi `POST http://localhost:8080/api/registrations` với `{"studentId": 1, "courseId": 2}`. Hệ thống sẽ tạo đăng ký và gọi nội bộ sang Course Service để trừ đi 1 số chỗ ngồi.
