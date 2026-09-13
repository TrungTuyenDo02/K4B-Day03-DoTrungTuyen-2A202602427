# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Đỗ Trung Tuyến
> **Mã Sinh Viên / Mã Học viên:** 2A202602427  
> **Chủ đề Lựa chọn:** Trợ lý quản lý đội bóng  

---



## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 3 / 5 |Trợ lý cần thực hiện nhiều bước nối tiếp nhau như: Kiểm tra danh sách thành viên => Đối chiếu kiếm tra xem ai còn chưa đóng quỹ. Tính toán số tiền mỗi người cần đóng trong tháng tiếp theo dựa trên số tiền chi tiêu các tháng trước (Tăng lên nếu chi tiêu trung bình cao hơn. Còn lại giữ nguyên) |
| **2. Tool Interaction** | 4 / 5 | Hệ thống có cần kết nối với CSDL thành viên, hệ thống quỹ, API thời tiết, công cụ đặt sân |
| **3. Dynamic Decision** | 3 / 5 | Các bước tiếp theo có phụ thuộc vào kết quả quan sát trước đó, tình hình thời tiết xấu => nhắc nhở đội cân nhắc hủy hoặc mang áo mưa hoặc đề xuất đổi lịch; số dư của quỹ không đủ để chi trả cho các trận đấu tiếp theo => thông báo cho các thành viên |
| **4. Long Horizon Goal** | 3 / 5 | Có mang tính dài hạn trong việc quản lý ngân sách, quản lý lịch sử đá của đội |
| **TỔNG ĐIỂM AGENTIC FIT** | **13 / 20** | *Tổng điểm > 12/20 → Bài toán khá phù hợp để triển khai dưới dạng Agentic System* 
---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật (Gemini, model `gemini-3.6-flash`):

```json
[
  {
    "step": 1,
    "query": "Cho mình xem hồ sơ và tình trạng đóng quỹ của thành viên mã TM001.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "member_query",
    "arguments": {
      "member_id": "TM001"
    },
    "observation": {
      "status": "SUCCESS",
      "member_id": "TM001",
      "data": {
        "full_name": "Nguyễn Văn Hùng",
        "position": "Tiền đạo",
        "status": "Đang tham gia",
        "monthly_fee": 100000,
        "fee_status": "Đã đóng tháng 9/2026",
        "debt_amount": 0
      }
    },
    "latency_ms": 1867.32
  },
  {
    "step": 2,
    "query": "Cho mình xem hồ sơ và tình trạng đóng quỹ của thành viên mã TM001.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Kết quả tra cứu thành viên TM001 (Nguyễn Văn Hùng): Vị trí: Tiền đạo, Trạng thái: Đang tham gia, Quỹ tháng: 100000, Tình trạng quỹ: Đã đóng tháng 9/2026, Số tiền còn nợ: 0.",
    "latency_ms": 10.0
  }
]
```

> Ghi chú: Log đầy đủ 13 Test Cases (24 sự kiện Thought → Action → Observation → Final Answer) được lưu tại `docs/trace_waterfall.json`, sinh ra khi chạy `python src/app.py --all` với `GeminiProvider` thật.

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` (`GEMINI_API_KEY`) và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini `gemini-3.6-flash`).
- **Tổng số Test Cases đã chạy thành công:** 13 / 13 test cases (mở rộng thêm 8 test case ngoài 5 test case tối thiểu yêu cầu, bao phủ đủ các loại: direct_query, single_tool_call, multi_tool_call, multi_step_tool_call, edge_case, out_of_scope).
- **Số lượt gọi Tool qua MCP Server chính xác:** 11 lượt (TC02, TC03, TC04, TC05, TC06 gọi trực tiếp qua Gemini API thật; TC07–TC12 gọi qua MCP Server sau khi Gemini tự động fallback về Mock Offline Provider do vượt hạn mức free tier — 5 requests/phút).
- **Ghi chú về Rate Limit:** Từ TC07 trở đi, Gemini free tier trả về lỗi `429 RESOURCE_EXHAUSTED` (giới hạn 5 requests/phút cho model `gemini-3.6-flash`), hệ thống đã tự động fallback về `MockOfflineProvider` đúng như thiết kế trong `src/providers.py`, MCP Server vẫn thực thi Tool thật (không phải dữ liệu giả lập cứng).
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
