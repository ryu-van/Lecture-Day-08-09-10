# Data contract — Lab Day 10

Tài liệu chi tiết hoá các cam kết về chất lượng, nguồn gốc và cấu trúc dữ liệu dựa trên [data_contract.yaml](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/contracts/data_contract.yaml).

---

## 1. Nguồn dữ liệu (Source Map)

| Nguồn | Phương thức Ingest | Failure mode chính | Metric / Alert |
|-------|-------------------|-------------------|----------------|
| **policy_refund_v4** | File export (CSV) | Chứa quy định hoàn tiền cũ 14 ngày (stale data) | `expectation[refund_no_stale_14d_window]` |
| **sla_p1_2026** | File export (CSV) | Thiếu thông tin ngày hiệu lực, định dạng không chuẩn | `expectation[effective_date_iso_yyyy_mm_dd]` |
| **it_helpdesk_faq** | File export (CSV) | Trùng lặp nội dung chunk, định dạng ngày tháng `DD/MM/YYYY` | `reason: duplicate_chunk_text` và `_normalize_effective_date` |
| **hr_leave_policy** | File export (CSV) | Xung đột chính sách 10 ngày phép cũ (2025) vs 12 ngày phép mới (2026) | `expectation[hr_leave_no_stale_10d_annual]` |

---

## 2. Schema Cleaned

| Cột | Kiểu | Bắt buộc | Ghi chú |
|-----|------|----------|---------|
| `chunk_id` | string | Có | Khóa chính duy nhất dạng SHA-256 hash đảm bảo tính duy nhất và idempotent |
| `doc_id` | string | Có | Thuộc `ALLOWED_DOC_IDS` (quy định trong hợp đồng) |
| `chunk_text` | string | Có | Nội dung văn bản của chunk (phải có độ dài tối thiểu là 8 ký tự, đã loại bỏ khoảng trắng thừa) |
| `effective_date` | date | Có | Ngày hiệu lực chuẩn hoá theo định dạng ISO `YYYY-MM-DD` |
| `exported_at` | datetime | Có | Thời gian hệ thống export bản ghi từ nguồn |

---

## 3. Quy tắc Quarantine vs Drop

- **Lưu trữ dữ liệu lỗi (Quarantine):** Các bản ghi vi phạm quy tắc làm sạch (như doc_id lạ, thiếu/sai định dạng effective_date, chứa placeholder nháp như `[TODO]`, hoặc trùng lặp văn bản) sẽ bị đưa vào tệp CSV riêng biệt tại thư mục `artifacts/quarantine/` theo định dạng `quarantine_<run_id>.csv`.
- **Drop:** Chúng tôi không âm thầm xóa (silent drop) dữ liệu. Mọi dòng dữ liệu lỗi đều được gán `reason` phân loại cụ thể và đẩy sang quarantine để dễ dàng đối chứng, truy vết lỗi từ hệ nguồn.
- **Merge & Approve:** Khi dữ liệu ở quarantine được bộ phận nghiệp vụ (SME) sửa đổi và cập nhật lại file export gốc, pipeline chạy lại sẽ tự động xử lý và merge các bản ghi hợp lệ mới vào ChromaDB.

---

## 4. Phiên bản & Canonical

- **Source of truth cho policy refund:** Canonical source chính là file văn bản [policy_refund_v4.txt](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/data/docs/policy_refund_v4.txt).
- **Mốc thời gian quy định:**
  - Chính sách nghỉ phép HR cũ (trước `2026-01-01`) sẽ bị quarantine hoàn toàn.
  - Cửa sổ hoàn trả của phòng CS phải được thống nhất ở mức **7 ngày làm việc** (phiên bản v4), thay vì 14 ngày làm việc của phiên bản v3 cũ.
