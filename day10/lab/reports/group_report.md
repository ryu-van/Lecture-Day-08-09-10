# Báo Cáo Nhóm — Lab Day 10: Data Pipeline & Data Observability

**Tên nhóm:** AI Data Operations Group  
**Thành viên:**
| Tên | Vai trò (Day 10) | Email |
|-----|------------------|-------|
| Nguyễn Văn A | Ingestion / Raw Owner | a.nguyen@example.com |
| Trần Thị B | Cleaning & Quality Owner | b.tran@example.com |
| Lê Văn C | Embed & Idempotency Owner | c.le@example.com |
| Phạm Văn D | Monitoring / Docs Owner | d.pham@example.com |

**Ngày nộp:** 2026-06-10  
**Repo:** `ryu-van/Lecture-Day-08-09-10`  

---

## 1. Pipeline tổng quan

Nguồn dữ liệu đầu vào là tệp export thô [policy_export_dirty.csv](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/data/raw/policy_export_dirty.csv). Quá trình xử lý chạy qua 4 bước khép kín: Ingest, Clean, Validate (Expectation Suite), và Embed (Idempotent Chroma).

**Lệnh chạy một dòng:**
```bash
python etl_pipeline.py run
```
Mỗi phiên chạy được định danh bởi một `run_id` duy nhất sinh tự động theo định dạng UTC timestamp (ví dụ: `2026-06-10T07-20Z`).

---

## 2. Cleaning & Expectation

Chúng tôi đã bổ sung **3 quy tắc làm sạch mới** và **2 quy tắc kiểm định (expectations) mới** vào hệ thống:
1. **Rule 7: Whitespace normalization:** Chuẩn hoá các khoảng trắng thừa trong `chunk_text`.
2. **Rule 8: Placeholder content check:** Cô lập các chunk chứa nội dung nháp (ví dụ: `[TODO]`, `[insert]`, `<placeholder>`, `[draft]`).
3. **Rule 9: Future effective date check:** Cô lập các dòng có ngày hiệu lực quá xa trong tương lai (sau `2028-12-31`).
4. **Expectation 7: Max quarantine ratio:** Halt pipeline nếu tỷ lệ dòng lỗi/cô lập > 60%.
5. **Expectation 8: Doc distribution check:** Cảnh báo (warn) nếu thiếu bất kỳ danh mục tri thức bắt buộc nào.

### 2a. Bảng metric_impact

| Rule / Expectation mới | Trước (số liệu) | Sau / khi inject (số liệu) | Chứng cứ |
|-----------------------------------|------------------|-----------------------------|-------------------------------|
| `placeholder_content` (Rule 8) | 0 quarantine | 1 quarantined (nếu có "[TODO]") | `reason: placeholder_content` |
| `future_effective_date` (Rule 9) | 0 quarantine | 1 quarantined (nếu date > 2028) | `reason: future_effective_date` |
| `max_quarantine_ratio_60` (E7) | 0.0 quarantine ratio | 0.40 quarantine ratio | `expectation[max_quarantine_ratio_60] OK` |
| `doc_distribution_check` (E8) | OK | OK | `expectation[doc_distribution_check] OK` |

---

## 3. Before / after ảnh hưởng retrieval hoặc agent

### Kịch bản inject
Chúng tôi cố ý tiêm dữ liệu lỗi bằng cách chạy pipeline bỏ qua sửa lỗi tự động và bỏ qua kiểm định:
```bash
python etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate
```

### Kết quả định lượng
Kết quả đánh giá tri thức truy xuất (retrieval evaluation):
- **Trước (Clean):** Câu hỏi về hoàn tiền (`q_refund_window`) trả về câu trả lời chuẩn 7 ngày của phiên bản v4, cột `hits_forbidden` bằng **`no`**.
- **Sau khi inject (Corrupted):** Câu hỏi hoàn tiền truy xuất trúng chunk lỗi 14 ngày phép (policy v3 cũ), cột `hits_forbidden` chuyển sang **`yes`**. Điều này chứng minh nếu không có data quality gate, Agent sẽ đọc sai thông tin.

Dẫn link chi tiết:
- [Kết quả khi chạy Sạch](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/artifacts/eval/before_after_eval.csv)
- [Kết quả khi bị Lỗi (Inject)](file:///d:/tai%20nguyen/VinAi/Lecture-Day-08-09-10/day10/lab/artifacts/eval/after_inject_bad.csv)

---

## 4. Freshness & monitoring

- **SLA chọn:** 24 giờ kể từ thời điểm dữ liệu được export khỏi hệ nguồn (`exported_at`).
- **Ý nghĩa:**
  - `PASS`: Dữ liệu mới cập nhật dưới 24h, an toàn sử dụng.
  - `WARN`: Dữ liệu từ 24h - 48h, hệ thống cảnh báo cần lập lịch đồng bộ.
  - `FAIL`: Vượt quá 48h, hệ thống kích hoạt cảnh báo SLA trễ. Dữ liệu thô trong lab do xuất từ tháng 4 nên khi chạy freshness check bị báo `FAIL` (age = 1463 giờ).

---

## 5. Liên hệ Day 09

Dữ liệu sau khi embed được đồng bộ trực tiếp vào ChromaDB collection `day10_kb`. Tệp index này cung cấp corpus sạch trực tiếp cho Retriever worker trong hệ thống Multi-agent của Day 09. Nhờ cơ chế publish boundary tự động prune (xóa vector cũ không còn trong CSV), chúng tôi tránh được hiện tượng Agent tham chiếu nhầm tài liệu cũ đã lỗi thời.

---

## 6. Rủi ro còn lại & việc chưa làm
- Cần phát triển thêm dashboard giao diện web hiển thị trực quan các biểu đồ phân bổ distribution của document IDs.
- Cấu hình gửi cảnh báo tự động thông qua webhook lên kênh chat Slack khi có sự cố.
