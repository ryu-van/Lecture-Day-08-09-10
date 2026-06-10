# Quality report — Lab Day 10

**run_id:** `2026-06-10T07-20Z` (Clean) vs `inject-bad` (Corrupted)  
**Ngày:** 2026-06-10

---

## 1. Tóm tắt số liệu

| Chỉ số | Trước (Corrupted: `inject-bad`) | Sau (Clean: `2026-06-10T07-20Z`) | Ghi chú |
|--------|---------------------------------|----------------------------------|---------|
| raw_records | 10 | 10 | Dữ liệu thô từ nguồn |
| cleaned_records | 6 | 6 | Số bản ghi hợp lệ nạp thành công |
| quarantine_records | 4 | 4 | Số bản ghi bị cô lập để điều tra |
| Expectation halt? | **FAIL (Halt)** (but skipped via flag) | **OK (Pass)** | Kết quả chạy kiểm tra chất lượng |

---

## 2. Before / after retrieval (bắt buộc)

Dẫn link kết quả đánh giá retrieval:
- [Kết quả khi chạy Sạch (Clean)](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/artifacts/eval/before_after_eval.csv)
- [Kết quả khi bị Lỗi (Corrupted)](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/artifacts/eval/after_inject_bad.csv)

### Câu hỏi then chốt: refund window (`q_refund_window`)
- **Khi bị Lỗi (Corrupted):**
  - `top1_doc_id`: `policy_refund_v4`
  - `top1_preview`: *"Yêu cầu hoàn tiền được chấp nhận trong vòng 14 ngày làm việc kể từ xác nhận đơn..."*
  - `contains_expected`: `yes`
  - `hits_forbidden`: **`yes`** (Lỗi nghiêm trọng: trả về thông tin stale "14 ngày làm việc" bị cấm).
- **Khi chạy Sạch (Clean):**
  - `top1_doc_id`: `policy_refund_v4`
  - `top1_preview`: *"Yêu cầu được gửi trong vòng 7 ngày làm việc kể từ thời điểm xác nhận đơn hàng."*
  - `contains_expected`: `yes`
  - `hits_forbidden`: **`no`** (Chính xác: thông tin 14 ngày đã được tự động sửa đổi thành 7 ngày).

### Versioning HR — `q_leave_version`
- **Kết quả:**
  - `top1_doc_id`: `hr_leave_policy`
  - `top1_preview`: *"Nhân viên dưới 3 năm kinh nghiệm được 12 ngày phép năm theo chính sách 2026."*
  - `contains_expected`: `yes`
  - `hits_forbidden`: `no`
  - `top1_doc_expected`: `yes` (Lấy chính xác thông tin mới 12 ngày của năm 2026, loại bỏ bản nháp 10 ngày phép của năm 2025).

---

## 3. Freshness & Monitor
- **Kết quả `freshness_check`:** `FAIL`
- **Chi tiết:** `{"latest_exported_at": "2026-04-10T08:00:00", "age_hours": 1463.341, "sla_hours": 24.0, "reason": "freshness_sla_exceeded"}`
- **Giải thích:** Dữ liệu nguồn sử dụng cho bài lab được xuất từ ngày `2026-04-10`, thời gian trôi qua đã vượt quá ngưỡng Freshness SLA 24 giờ quy định trong hợp đồng dữ liệu. Hệ thống tự động kích hoạt cảnh báo SLA trễ.

---

## 4. Corruption Inject (Sprint 3)
- **Mô tả hành vi tiêm lỗi:** Chạy pipeline với tùy chọn `--no-refund-fix --skip-validate`.
- **Cách phát hiện:**
  - Quy tắc kiểm định `expectation[refund_no_stale_14d_window]` lập tức phát hiện có 1 bản ghi chứa "14 ngày làm việc" và báo lỗi `FAIL (halt)`.
  - Quá trình đánh giá retrieval ghi nhận cột `hits_forbidden` chuyển sang `yes` cho câu hỏi truy vấn hoàn tiền.

---

## 5. Hạn chế & việc chưa làm
- Chưa cấu hình tự động gửi cảnh báo lên Slack/Teams khi kiểm tra Freshness thất bại.
- Cần xây dựng thêm cơ chế tự động rollback dữ liệu vector store về snapshot an toàn trước đó nếu validate bị halt.
