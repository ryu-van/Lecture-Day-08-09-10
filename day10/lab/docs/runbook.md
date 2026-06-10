# Runbook — Lab Day 10 (Sự cố dữ liệu tri thức)

Hướng dẫn vận hành khi phát hiện Agent trả về thông tin tri thức cũ hoặc sai lệch chính sách của CS / IT / HR.

---

## Symptom (Triệu chứng)
- Người dùng hoặc Agent nhận được câu trả lời sai lệch nghiệp vụ thực tế. Ví dụ:
  - Agent trả lời chính sách hoàn trả là **14 ngày làm việc** (trong khi quy định v4 mới nhất là **7 ngày làm việc**).
  - Agent trả lời số ngày nghỉ phép là **10 ngày** (trong khi chính sách 2026 mới là **12 ngày**).

---

## Detection (Phát hiện)
Các chỉ số cảnh báo sớm trên hệ thống giám sát dữ liệu (Observability):
1. **Freshness SLA:** Kiểm tra manifest thấy `freshness_check=FAIL` (dữ liệu nạp trễ hơn 24 giờ so với thời điểm xuất bản).
2. **Expectation fail:** Pipeline bị dừng đột ngột (halt) hoặc sinh cảnh báo (warn). Ví dụ: `expectation[refund_no_stale_14d_window] FAIL`.
3. **Retrieval Eval:** Chỉ số `hits_forbidden` trong file đánh giá retrieval tự động trả về `yes`.

---

## Diagnosis (Chẩn đoán)

| Bước | Việc làm | Kết quả mong đợi |
|------|----------|------------------|
| 1 | Kiểm tra manifest JSON chạy gần nhất tại `artifacts/manifests/` | Xác định xem pipeline có bị bỏ qua bước validate (`skipped_validate=true`) hoặc không áp dụng bộ sửa lỗi tự động (`no_refund_fix=true`) hay không. |
| 2 | Mở file quarantine tại `artifacts/quarantine/` | Xem nguyên nhân dòng dữ liệu bị cô lập (ví dụ: `stale_hr_policy_effective_date` do ngày hiệu lực quá cũ, `placeholder_content` do còn chứa nháp `[TODO]`). |
| 3 | Chạy đánh giá độc lập: `python eval_retrieval.py` | Kiểm tra xem top-k retrieve có chứa từ khóa bị cấm hay không bằng cách xem cột `hits_forbidden` trong file eval. |

---

## Mitigation (Giảm thiểu tạm thời)
1. **Rerun Standard Pipeline:** Chạy lại ngay lập tức pipeline tiêu chuẩn để kích hoạt lại các rule tự động thay thế và bộ expectation suite:
   ```bash
   python etl_pipeline.py run
   ```
2. **Rollback Data Collection:** Nếu dữ liệu mới nạp bị lỗi nặng, rollback vector store về phiên bản sạch gần nhất (Restore snapshot Chroma collection).
3. **Báo cáo sự cố:** Liên hệ với `AI_Data_Operations` qua kênh `#alerts-data-observability` để kiểm tra file export thô từ phía hệ nguồn.

---

## Prevention (Phòng ngừa lâu dài)
- Thiết lập tự động chặn triển khai (deployment gate) nếu pipeline ETL bị halt.
- Đồng bộ hoá chặt chẽ schema và data contract với đội ngũ phát triển sản phẩm ở thượng nguồn để tránh lỗi parser.
- Tự động hóa việc chạy kiểm tra `freshness_check` định kỳ qua cron job.
