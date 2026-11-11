# Team

## Thông tin nhóm

- Tên nhóm: Zolo
- Lớp: L3A
- Repo nhóm: `K5-L3A-DAY03-Zolo-ResearchAgentToolEval`
- URL repo, nhánh nộp, commit chốt: https://github.com/phamquynhanh-17/K5-L3A-DAY03-Zolo-ResearchAgentToolEval, `main`, `980e0b4`

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Phạm Quỳnh Anh | 2A202603671 | quynhanh112125@gmail.com | phamquynhanh-17 | Team Lead / Full-stack AI Engineer |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

- File báo cáo cá nhân: [`report/team/2A202603671_PhamQuynhAnh.md`](report/team/2A202603671_PhamQuynhAnh.md)

## Phạm Quỳnh Anh - 2A202603671

### Phần việc phụ trách

- Thiết lập môi trường, cấu hình provider (Groq OpenAI-compatible `openai/gpt-oss-120b`), chạy baseline `v0` và phân tích lỗi (CP1).
- Thiết kế và tối ưu hóa `artifacts/system_prompt.md` và `artifacts/tools.yaml` qua 3 vòng lặp thực nghiệm `v1`, `v2`, `v3` (CP2).
- Phát triển công cụ mới `github_search` (`tools/github_search/tool.py` & `TOOL.md`) và hoàn thiện toàn bộ 17 unit tests trong `tests/test_tools_todo.py` đạt 84/84 passed, 0 skipped (CP3 + Bonus Test Challenge).
- Xây dựng bộ 10 eval cases của nhóm (`data/eval_group.json`: 5 single-turn + 5 multi-turn) đạt 10/10 PASS (CP4).
- Xây dựng giao diện Streamlit UI (`starter_v0/app.py`), chạy phiên live chat 5 lượt (`starter_v0/transcripts/`) và viết báo cáo nhóm & cá nhân (CP5).

### Đóng góp cụ thể

- Sửa `starter_v0/providers/openai_provider.py` hỗ trợ biến môi trường `OPENAI_BASE_URL` và `OPENAI_MODEL`.
- Tối ưu hóa `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, nâng độ chính xác từ 70% (`v0`) lên 90% (`v2`) trên bộ `eval_base.json` và 100% (`10/10`) trên bộ `eval_group.json`.
- Viết tool mới `starter_v0/tools/github_search/` tích hợp GitHub REST API có kiểm tra đầu vào chặt chẽ và xử lý lỗi an toàn (`err("github_search", exc)`).
- Hoàn thành 100% unit test trong `starter_v0/tests/test_tools_todo.py` (84 passed, 0 failed, 0 skipped).
- Xây dựng ứng dụng web tương tác `starter_v0/app.py` bằng Streamlit hỗ trợ chọn câu hỏi mẫu, xem chi tiết từng lệnh gọi tool và tải file transcript JSON.

### Bằng chứng

- Run logs:
  - `starter_v0/runs/v0_B_base_openai_20261110T220643666499.json`
  - `starter_v0/runs/v1_B_base_openai_20261110T221054697913.json`
  - `starter_v0/runs/v2_B_base_openai_20261110T222359630403.json`
  - `starter_v0/runs/v3_B_base_openai_20261111T075558766207.json`
  - `starter_v0/runs/v3_B_group_openai_20261111T080754277941.json`
- Code & Tests:
  - `starter_v0/tools/github_search/tool.py`, `starter_v0/tools/github_search/TOOL.md`
  - `starter_v0/tests/test_tools_todo.py`
  - `starter_v0/data/eval_group.json`
  - `starter_v0/app.py`
