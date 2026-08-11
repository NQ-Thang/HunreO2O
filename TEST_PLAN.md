# Hướng dẫn chi tiết Kịch bản Test (Nguyễn Văn Chiến - ĐH13C1)

Chào bạn, tôi đã chuẩn bị sẵn một **script tự động (test.ps1)** và tài liệu hướng dẫn này để bạn có thể test dễ dàng nhất, đúng chuẩn theo mọi yêu cầu.

## 1. File Script Test Tự động (`test.ps1`)
Tôi đã viết đoạn script chạy test vào file `test.ps1` (`d:\Intel\Project\crs-microservices\course-service\test.ps1`). Script này sẽ:
- **Tự động tạo môn học** bằng PowerShell.
- Lấy `id` môn học vừa tạo và thực hiện bắn tuần tự các API tương ứng với các Test từ 1 đến 13 (ngoại trừ test server rớt và test đồng thời).
- Bắt lỗi và in ra Terminal bằng các màu sắc dễ nhìn để bạn đối chiếu kỳ vọng.

**Cách chạy script:** 
Tại cửa sổ dòng lệnh PowerShell, bạn điều hướng vào thư mục `course-service` và gõ `.\test.ps1`. Xem kết quả hiển thị trên màn hình.

---

## 2. Hướng dẫn Test Thủ công qua Postman (Chi tiết từng bước)

Dưới đây là tài liệu chi tiết nếu bạn cần click tay qua Postman để minh chứng.
> [!TIP]
> Tôi đã dọn dẹp và tạo sẵn cho bạn một môn học duy nhất có **ID = 12**. Bạn chỉ cần bê nguyên các đường link bên dưới dán vào Postman là chạy được 100%.

### A. Nhóm Test API nội bộ Course-service (Port 8082)
- **Test 1 - Trừ chỗ:** Gọi `PATCH http://localhost:8082/internal/courses/12/reserve-seat`. 
  - *Kỳ vọng:* Status 200, trường `soChoConLai` trả về giảm đi 1 (còn 1).
  - 🔍 *Check Database:* Mở `course_db`, select bảng `course`, bạn sẽ thấy `so_cho_con_lai` tụt xuống 1.
- **Test 2 - Test hết chỗ:** Gọi tiếp lệnh trên 2 lần nữa. Lần 2 sẽ trừ chỗ về 0. Lần 3 sẽ trả về lỗi.
  - *Kỳ vọng:* Status 409 Conflict, Body: `{"message": "Mon hoc da het cho, khong the dang ky"}`.
  - 🔍 *Check Database:* Mở bảng `course`, `so_cho_con_lai` dừng đúng ở 0, không bị âm (-1).
- **Test 3 - Hoàn chỗ:** Gọi `PATCH http://localhost:8082/internal/courses/12/release-seat`.
  - *Kỳ vọng:* Status 200, `soChoConLai` tăng lên 1. Gọi liên tiếp cũng không được vượt quá `soChoToiDa`.

### B. Nhóm Test Luồng gọi chéo Registration-service (Port 8083)
- **Test 4 - Đăng ký thành công:** Gọi `POST http://localhost:8083/registrations` với body `{"studentId":1, "courseId":12}`.
  - *Kỳ vọng:* Status 201 Created. 
  - 🔍 *Check Database 1:* Mở `registration_db` bảng `registration`, sinh ra bản ghi mới có `trang_thai = 'DA_DANG_KY'`.
  - 🔍 *Check Database 2:* Mở `course_db` bảng `course`, số chỗ lại bị trừ đi 1.
- **Test 5 - Đăng ký trùng:** Gọi lại y hệt request Test 4 một lần nữa.
  - *Kỳ vọng:* Status 409, Body: `{"message": "Sinh vien da dang ky mon hoc nay"}`.
- **Test 6 - Hủy đăng ký:** Lấy ID đăng ký từ Test 4 (ví dụ `1`), gọi `DELETE http://localhost:8083/registrations/1`.
  - *Kỳ vọng:* Status 204 No Content / 200 OK. 
  - 🔍 *Check Database:* Mở `registration_db` bảng `registration` thấy đổi sang `DA_HUY`. Mở `course_db` thấy chỗ được trả lại (+1).
- **Test 7 & 8 - Môn hết chỗ / Không tồn tại:** Gọi đăng ký với `courseId` là `9999`.
  - *Kỳ vọng:* Status 404 hoặc 409 (Môn học không tồn tại).
- **Test 9 - Test Server rớt:** 
  - 🔍 *Hành động bổ sung:* Vào Terminal đang chạy `course-service` và nhấn `Ctrl + C` để tắt server.
  - Gọi lại request đăng ký ở Test 4.
  - *Kỳ vọng:* Trả về lỗi 500 kèm thông báo "Khong the ket noi den course-service" thay vì treo server. Đừng quên bật lại server sau khi test xong!

### C. Nhóm Test Tìm kiếm & Phân trang (Port 8082)
- **Test 10 - Tìm kiếm có dấu:** Gọi `GET http://localhost:8082/courses?keyword=Java&page=0&size=5`.
  - *Kỳ vọng:* Trả về mảng JSON phân trang chính xác.
- **Test 11 - Phân trang sai:** Gọi `GET http://localhost:8082/courses?page=-1`.
  - *Kỳ vọng:* Status 500/400 (Lỗi do Page index < 0).

### D. Nhóm Test Race Condition (Tranh chấp dữ liệu)
*Cách Test cướp chỗ (Giành giật chỗ cuối cùng):*
1. Mở Postman, gọi API Release Seat hoặc Reserve Seat sao cho môn ID `12` chỉ còn đúng 1 chỗ.
2. Mở 2 Tab trong Postman. Tab 1 set `studentId: 10`, Tab 2 set `studentId: 11`. (Đều dùng courseId: 12)
3. **Mẹo Postman:** Lưu 2 request này vào cùng 1 Folder. Nhấp phải vào Folder chọn **Run folder**. Check chọn 2 request đó, số lần chạy (Iterations) = 1, không Delay. Nhấn Run.
4. *Kỳ vọng:* Chỉ 1 request báo 201, request còn lại báo 409 Hết chỗ.
5. 🔍 *Check Database:* Mở `course_db` check bảng `course`, `so_cho_con_lai` phải bằng 0 (không bao giờ bị thủng xuống -1).
