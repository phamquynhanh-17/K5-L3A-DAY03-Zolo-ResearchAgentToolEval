from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)

st.set_page_config(
    page_title="Zolo Research Agent — Day 03 Tool Eval",
    page_icon="🔬",
    layout="wide",
)

SAMPLE_PROMPTS = [
    "Tìm các repository GitHub nhiều sao nhất về RAG.",
    "Tra cứu quy định nội bộ của công ty về bảo mật dữ liệu cá nhân (data privacy).",
    "Tìm giúp mình 3 bài báo khoa học trên arXiv về Mixture of Experts.",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Đăng bản tin AI hôm nay lên Telegram giúp mình",
]

with st.sidebar:
    st.title("🔬 Zolo Research Agent")
    st.caption("K5-L3A · Day 03 Research Agent Tool Eval")

    provider_name = st.selectbox(
        "Model Provider",
        options=["openai", "openrouter", "gemini", "anthropic", "ollama"],
        index=0,
        help="Groq được kết nối qua OpenAI-compatible provider.",
    )
    version_label = st.text_input("Artifact Version Label", value="v3")
    history_window = st.slider("History Window (turns)", min_value=1, max_value=10, value=5)
    max_tool_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=6, value=4)

    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    artifact_ver = build_artifact_version(version_label, system_prompt_path, tools_path)
    st.code(artifact_ver.artifact_version, language="text")

    if st.button("🔄 New Chat Session", use_container_width=True):
        st.session_state.pop("messages", None)
        st.session_state.pop("history", None)
        st.session_state.pop("transcript", None)
        st.session_state.pop("transcript_path", None)
        st.rerun()

    st.divider()
    st.subheader("💡 Câu hỏi mẫu (Click để thử)")
    for sample in SAMPLE_PROMPTS:
        if st.button(sample, use_container_width=True):
            st.session_state["pending_prompt"] = sample

    st.divider()
    tool_decls = load_tool_declarations(tools_path)
    with st.expander(f"🛠️ Danh sách Tools ({len(tool_decls)})", expanded=False):
        for t in tool_decls:
            st.markdown(f"**`{t['name']}`** — {t.get('description', '')}")


def init_session() -> None:
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "history" not in st.session_state:
        st.session_state["history"] = []
    if "transcript" not in st.session_state:
        provider = make_provider(provider_name)
        selected_model = getattr(provider, "default_model", None)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = "_".join([safe_slug(version_label), safe_slug(provider_name), timestamp])
        transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
        st.session_state["transcript_path"] = transcript_path
        st.session_state["transcript"] = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_ver),
            "provider": provider_name,
            "model": selected_model,
            "system_prompt": str(system_prompt_path),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [],
        }


init_session()

st.header("🔬 Zolo Research Agent — Interactive Tool-Calling Demo")
st.markdown(
    "Trợ lý nghiên cứu đa nguồn: **GitHub Repositories (`github_search`)**, **arXiv Papers (`papers`, `paper_text`)**, "
    "**Company Policy (`policy`)**, **Web & Social (`lookup`, `fetch`, `timeline`, `social_search`)**, "
    "tự động hỏi lại khi thiếu thông tin (**`clarify`**) và xin xác nhận an toàn trước khi gửi (**`send`**)."
)

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        for ev in msg.get("tool_events", []):
            with st.expander(f"🔧 Tool Call: `{ev['tool']}`", expanded=False):
                st.markdown("**Arguments:**")
                st.json(ev.get("args", {}))
                st.markdown("**Result:**")
                st.json(ev.get("result", {}))

user_input = st.chat_input("Nhập yêu cầu nghiên cứu của bạn...")
if "pending_prompt" in st.session_state:
    user_input = st.session_state.pop("pending_prompt")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Đang phân tích và gọi công cụ..."):
            system_prompt = system_prompt_path.read_text(encoding="utf-8")
            openai_tools = to_openai_tools(load_tool_declarations(tools_path))
            provider = make_provider(provider_name)

            turn_index = len(st.session_state["transcript"]["turns"]) + 1
            messages = [
                {"role": "system", "content": system_prompt},
                *trim_history(st.session_state["history"], history_window),
                {"role": "user", "content": user_input},
            ]
            turn_record: dict[str, Any] = {
                "turn_index": turn_index,
                "started_at": now_iso(),
                "user": user_input,
                "status": "started",
                "assistant_text": None,
                "rounds": [],
                "tool_events": [],
            }
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=None,
                    max_tool_rounds=max_tool_rounds,
                )
                turn_record.update(result)
                assistant_text = result["assistant_text"]
                tool_events = result.get("tool_events", [])
                for ev in tool_events:
                    with st.expander(f"🔧 Tool Call: `{ev['tool']}`", expanded=True):
                        st.markdown("**Arguments:**")
                        st.json(ev.get("args", {}))
                        st.markdown("**Result:**")
                        st.json(ev.get("result", {}))
                st.markdown(assistant_text)
                st.session_state["history"].append({"role": "user", "content": user_input})
                st.session_state["history"].append({"role": "assistant", "content": assistant_text})
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                })
            except Exception as exc:
                err_msg = f"{type(exc).__name__}: {str(exc)}"
                turn_record.update({"status": "provider_error", "error": err_msg})
                st.error(err_msg)

            turn_record["ended_at"] = now_iso()
            st.session_state["transcript"]["turns"].append(turn_record)
            write_transcript(st.session_state["transcript_path"], st.session_state["transcript"])

if st.session_state["transcript"]["turns"]:
    with st.sidebar:
        st.divider()
        st.subheader("📄 Transcript JSON")
        st.caption(f"Saved: `{st.session_state['transcript_path'].name}`")
        st.download_button(
            "⬇️ Tải Transcript JSON",
            data=json.dumps(st.session_state["transcript"], ensure_ascii=False, indent=2),
            file_name=st.session_state["transcript_path"].name,
            mime="application/json",
            use_container_width=True,
        )

