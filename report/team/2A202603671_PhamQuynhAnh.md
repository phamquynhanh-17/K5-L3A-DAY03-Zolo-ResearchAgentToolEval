# Báo cáo cá nhân — Phạm Quỳnh Anh - 2A202603671

## 1. Thông tin thành viên

- Họ tên: Phạm Quỳnh Anh
- MSSV: 2A202603671
- Email: quynhanh112125@gmail.com
- GitHub: `phamquynhanh-17`
- Nhóm: Zolo (Lớp L3A)

## 2. Phần việc phụ trách

Là thành viên thực hiện toàn bộ quy trình từ CP1 đến CP5 của nhóm Zolo:
1. **CP1 (Setup & Baseline v0):** Cấu hình môi trường Python, kết nối Groq (`openai/gpt-oss-120b`) qua `OpenAIProvider`, chạy preflight, chạy baseline `v0` và phân loại 6 ca lỗi ban đầu.
2. **CP2 (Tối ưu hóa v1 $\rightarrow$ v3):** Thực hiện vòng lặp giả thuyết – sửa đổi – đo lường trên `system_prompt.md` và `tools.yaml`, ghi nhận đầy đủ vào `version_log.csv`.
3. **CP3 (Tool mới & Unit Tests):** Thiết kế và lập trình tool mới `github_search` (`tools/github_search/`), đăng ký vào `tools/__init__.py` và `tools.yaml`, đồng thời hoàn thiện toàn bộ 17 unit test trong `tests/test_tools_todo.py` (đạt 84 passed, 0 failed, 0 skipped).
4. **CP4 (Eval nhóm 10 cases):** Xây dựng 5 single-turn cases (`G01`–`G05`) và 5 multi-turn cases (`G06`–`G10`) trong `data/eval_group.json`, kiểm thử đạt 10/10 PASS (100%).
5. **CP5 (UI, Live Chat & Báo cáo):** Xây dựng giao diện Streamlit (`starter_v0/app.py`), thực hiện phiên hội thoại thực tế lưu transcript JSON và hoàn thiện báo cáo nhóm + cá nhân.

## 3. Đóng góp cụ thể

- **Tối ưu Prompt & Tool Declarations (`artifacts/system_prompt.md`, `artifacts/tools.yaml`):**
  - Ở `v1`: Loại bỏ chỉ dẫn xấu của starter (đoán mò handle `sama`, tự bịa URL, tự gửi không cần xác nhận, ép chỉ gọi 1 tool). Thêm nguyên tắc gọi `clarify(response_type="text")` khi thiếu thông tin và `clarify(response_type="yes_no")` trước khi gửi $\rightarrow$ Điểm tăng từ **14/20 (0.70)** lên **17/20 (0.85)**, multi-turn đạt **1.00**.
  - Ở `v2`: Viết lại toàn bộ `description` trong `tools.yaml` (nêu rõ khi nào dùng / không dùng, quy ước `query` của `lookup` chỉ chứa từ khóa cốt lõi không lặp lại `news`/`today`, ranh giới `send`) $\rightarrow$ Giải quyết triệt để lỗi dư từ khóa ở `R03` và `M02`, nâng điểm lên **18/20 (0.90)**.
  - Ở `v3`: Thử nghiệm nhấn mạnh đồng thời hai quy tắc (`yes_no` cho `send` và gọi song song cho `R13`) trong `system_prompt.md` $\rightarrow$ Điểm đạt **17/20 (0.85)** do phát sinh lỗi `samaltman` ở `R01`. Rút ra bài học thực nghiệm quan trọng về việc tách biệt từng thay đổi và neo rõ handle mapping (`sama`).
- **Phát triển Tool mới (`starter_v0/tools/github_search/`):**
  - Cài đặt hàm `github_search(query, sort="stars", max_results=5)` tra cứu kho mã nguồn mở qua GitHub REST API.
  - Kiểm tra chặt chẽ dữ liệu đầu vào từ model (`query` rỗng, `sort` ngoài tập `{"stars", "forks", "updated"}`, `max_results` ngoài khoảng `1..50`) và luôn trả về dictionary chuẩn qua `err("github_search", exc)` thay vì để văng ngoại lệ.
- **Hoàn thiện Unit Tests (`starter_v0/tests/test_tools_todo.py`):**
  - Viết đầy đủ 14 test cho các tool có sẵn (`clarify`, `format`, `send`, `lookup`, `fetch`, `timeline`, `social_search`, `policy`) và 3 test cho `github_search` (happy path, bad input, HTTP 403 error). Toàn bộ suite `pytest` đạt **84 passed, 0 failed, 0 skipped**.
- **Thiết kế 10 Eval Cases (`starter_v0/data/eval_group.json`):**
  - Bao phủ định tuyến tới tool mới `github_search` (`G01`, `G06`, `G08`), tra cứu học thuật `papers` (`G02`), lọc phân vùng `policy` (`G03`), hỏi lại khi thiếu arXiv ID (`G04`), câu hỏi khái niệm không dùng tool (`G05`), xác nhận trước khi gửi (`G07`), điền URL sau clarify (`G09`), và sửa `limit` nhiều lượt (`G10`). Kết quả chạy đạt **10/10 PASS (1.00)**.

## 4. Bằng chứng

- **Files đã tạo / chỉnh sửa:**
  - `starter_v0/artifacts/system_prompt.md`
  - `starter_v0/artifacts/tools.yaml`
  - `starter_v0/artifacts/version_log.csv`
  - `starter_v0/tools/github_search/tool.py` & `starter_v0/tools/github_search/TOOL.md`
  - `starter_v0/tools/__init__.py`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/data/eval_group.json`
  - `starter_v0/app.py` & `starter_v0/requirements.txt`
  - `report/team/group_report.md`
- **Run JSONs:**
  - `starter_v0/runs/v0_B_base_openai_20261110T220643666499.json`
  - `starter_v0/runs/v1_B_base_openai_20261110T221054697913.json`
  - `starter_v0/runs/v2_B_base_openai_20261110T222359630403.json`
  - `starter_v0/runs/v3_B_base_openai_20261111T075558766207.json`
  - `starter_v0/runs/v3_B_group_openai_20261111T080754277941.json`
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Sử dụng trợ lý coding AI để hỗ trợ viết khung unit test và giao diện Streamlit; tự kiểm tra lại bằng cách chạy trực tiếp `pytest -v` (84/84 xanh, offline với `fake_http`), chạy `run_eval.py` trên API thật (`provider_error_cases == 0`) và đối chiếu từng dòng log JSON.

## 5. Tự đánh giá

- **Điểm mạnh:** Hoàn thành đầy đủ tất cả 5 Checkpoint bắt buộc và phần Bonus Test Challenge (0 skipped toàn suite). Quy trình thực nghiệm tuân thủ chặt chẽ nguyên tắc evidence-driven, trung thực với số liệu log thực tế.
- **Bài học rút ra:** Phân biệt rõ vai trò của Unit Test (bảo vệ tầng code thực thi của tool trước input xấu/lỗi mạng) và Eval Suite (đo lường hành vi lựa chọn công cụ và tham số của mô hình LLM).
