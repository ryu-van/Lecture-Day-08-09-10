# Báo Cáo Cá Nhân — Lab Day 10: Data Pipeline & Observability

**Họ và tên:** Nguyễn Văn A  
**Vai trò:** Ingestion & Quality Owner  
**Ngày nộp:** 2026-06-10

---

## 1. Tôi phụ trách phần nào?

Trong ngày 10, tôi phụ trách phần xây dựng và mở rộng **Ingestion Pipeline** và **Expectation Suite** tại các file:
- [cleaning_rules.py](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/transform/cleaning_rules.py): Triển khai các quy tắc làm sạch dữ liệu (Rule 7, 8, 9).
- [expectations.py](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/quality/expectations.py): Thêm các quy tắc kiểm định chất lượng (E7, E8) và thay đổi signature hàm để nhận `raw_count`.
- [etl_pipeline.py](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/etl_pipeline.py): Đảm bảo luồng chạy chuyển giao số lượng bản ghi chính xác cho bộ kiểm định.

Tôi kết nối chặt chẽ với Lê Văn C (phụ trách phần nhúng vector) nhằm đảm bảo dữ liệu qua cổng chất lượng trước khi nạp vào Chroma DB.

---

## 2. Một quyết định kỹ thuật

Tôi quyết định thiết lập mức độ nghiêm trọng **`halt`** cho quy tắc **`max_quarantine_ratio_60`** (Tỉ lệ dữ liệu lỗi vượt quá 60%). 
Lý do: Nếu hơn 60% dữ liệu nguồn bị cô lập vào quarantine, chứng tỏ cấu trúc file xuất (schema) từ hệ thống nguồn đã bị thay đổi đột ngột (schema drift) hoặc file xuất bị lỗi mã hóa nghiêm trọng. Tiếp tục nhúng một lượng dữ liệu quá nhỏ sẽ làm mất lượng lớn thông tin nghiệp vụ, khiến Agent trả lời sai lệch hoàn toàn. Việc dừng (halt) ngay lập tức giúp bảo vệ tính toàn vẹn của cơ sở tri thức hiện tại.

---

## 3. Một lỗi hoặc anomaly đã xử lý

Khi chạy thử nghiệm với tập dữ liệu chứa các bản ghi lỗi, tôi phát hiện ra lỗi mã hóa Unicode (`UnicodeEncodeError`) do console môi trường Windows dùng bảng mã mặc định không hiển thị được ký tự mũi tên `→` trong log cảnh báo.
- **Phát hiện:** Log ghi lỗi `charmap codec can't encode character...` tại dòng in log của pipeline.
- **Xử lý:** Tôi đã chuẩn hóa các chuỗi in log của pipeline thành ký tự ASCII chuẩn (thay thế `→` thành `->` và viết không dấu các phần mô tả bổ sung trong log cảnh báo), đảm bảo đường ống chạy mượt mà trên mọi môi trường shell mà không bị crash giữa chừng.

---

## 4. Bằng chứng trước / sau

**Run ID:** `2026-06-10T07-20Z` (Sạch) vs `inject-bad` (Lỗi)

Dòng kết quả đánh giá truy xuất câu hỏi `q_refund_window` tương ứng:
- **Trước (Khi bị lỗi - `inject-bad`):**
  `q_refund_window, ..., policy_refund_v4, ..., contains_expected: yes, hits_forbidden: yes`
- **Sau (Khi chạy sạch - `2026-06-10T07-20Z`):**
  `q_refund_window, ..., policy_refund_v4, ..., contains_expected: yes, hits_forbidden: no`

---

## 5. Cải tiến tiếp theo

Nếu có thêm 2 giờ, tôi sẽ viết một script Pytest tự động kiểm tra tích hợp chạy end-to-end cho cả 2 kịch bản (chạy sạch và chạy lỗi) để đảm bảo chất lượng kiểm định luôn được kiểm tra tự động trước mỗi lần commit code lên Git.
