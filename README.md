# Course Service Microservice

**Người thực hiện:** Nguyễn Văn Chiến  

## 🚀 Chức năng chính (Features)
Dự án được xây dựng dựa trên kiến trúc phân tầng 3 lớp (Controller - Service - Repository) chuẩn Spring Boot.

* **Kiến trúc & Data Contract**: Sử dụng hoàn toàn `CourseDTO` để giao tiếp giữa client và server, ẩn giấu cấu trúc Entity thật bên trong CSDL.
* **CRUD Course (RESTful API)**: Đầy đủ 5 endpoint thao tác trên môn học:
  * `GET /courses`: Xem danh sách tất cả các môn học.
  * `GET /courses/{id}`: Tra cứu thông tin chi tiết của 1 môn học theo ID.
  * `POST /courses`: Thêm mới một môn học (tự động thiết lập số chỗ còn lại).
  * `PUT /courses/{id}`: Cập nhật thông tin môn học (giữ nguyên số chỗ còn lại theo nghiệp vụ).
  * `DELETE /courses/{id}`: Xóa môn học khỏi hệ thống.
* **Validation mạnh mẽ**: Xác thực đầu vào (Bean Validation) đối với các trường bắt buộc, kiểm tra số lượng phải lớn hơn 0 (Tín chỉ, số chỗ tối đa). Bắt lỗi trùng tên môn học.
* **Xử lý lỗi (Global Exception Handling)**: Sử dụng `@RestControllerAdvice` để format tất cả lỗi trả về đồng nhất dưới định dạng JSON (mã lỗi `400 Bad Request`, `404 Not Found`).
* **Database**: Tương tác trực tiếp và lưu trữ an toàn trên MySQL (`course_db`).
