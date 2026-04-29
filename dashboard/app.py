"""Optional Streamlit dashboard for Compute Cost Simulator receipt logs.

Run with:
    streamlit run dashboard/app.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError as exc:  # pragma: no cover - only reached without optional extra.
    raise SystemExit(
        "Streamlit is required for the optional dashboard. Install it with:\n"
        '  pip install -e ".[dashboard]"'
    ) from exc

from ccs import summarize_logs


DEFAULT_LOG_PATH = "logs/ccs_session.jsonl"


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                receipts.append(json.loads(line))
    return receipts


def _receipt_log_from_upload(uploaded_file: Any) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for raw_line in uploaded_file.getvalue().decode("utf-8").splitlines():
        if raw_line.strip():
            receipts.append(json.loads(raw_line))
    return receipts


def _remaining_budget(receipts: list[dict[str, Any]]) -> float | None:
    for receipt in reversed(receipts):
        if "budget_remaining_after" in receipt:
            return float(receipt["budget_remaining_after"])
    for receipt in reversed(receipts):
        if "budget_total" in receipt:
            total_cost = sum(float(item.get("cost", 0.0)) for item in receipts)
            return round(float(receipt["budget_total"]) - total_cost, 6)
    return None


def _looks_like_ai_receipt(receipt: dict[str, Any]) -> bool:
    category = str(receipt.get("category", "")).lower()
    model = str(receipt.get("model", "")).lower()
    model_size = str(receipt.get("model_size", "")).lower()
    task = str(receipt.get("task", "")).lower()
    ai_markers = ("ai", "llm", "rag", "chat", "assistant", "embedding")
    return (
        category == "llm"
        or any(marker in category for marker in ai_markers)
        or any(marker in model for marker in ai_markers)
        or any(marker in model_size for marker in ai_markers)
        or any(marker in task for marker in ai_markers)
    )


def _ai_vs_modeling_cost(receipts: list[dict[str, Any]]) -> dict[str, float]:
    total_cost = sum(float(receipt.get("cost", 0.0)) for receipt in receipts)
    ai_cost = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if _looks_like_ai_receipt(receipt)
    )
    modeling_cost = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if receipt.get("category") == "modeling"
    )
    other_compute_cost = max(total_cost - ai_cost - modeling_cost, 0.0)
    ai_share = ai_cost / total_cost if total_cost else 0.0
    return {
        "ai_cost": ai_cost,
        "modeling_cost": modeling_cost,
        "other_compute_cost": other_compute_cost,
        "ai_share": ai_share,
    }


def _show_log_help() -> None:
    st.info(
        "No receipts loaded yet. Generate a dashboard log by running:\n\n"
        "```bash\n"
        "python examples/flagship_budget_failure_demo.py\n"
        "python examples/intro_modeling_demo.py\n"
        "python examples/llm_token_demo.py\n"
        "```\n\n"
        f"Then load `{DEFAULT_LOG_PATH}` here."
    )


st.set_page_config(page_title="Compute Cost Simulator", layout="wide")
st.title("Compute Cost Simulator Dashboard")
st.caption("All costs shown here are simulated pedagogical estimates, not real billing.")

with st.sidebar:
    st.header("Receipt Log")
    uploaded_file = st.file_uploader("Upload JSONL receipt log", type=["jsonl"])
    path_text = st.text_input("Or enter a JSONL path", value=DEFAULT_LOG_PATH)

receipts: list[dict[str, Any]] = []
source_label = ""

try:
    if uploaded_file is not None:
        receipts = _receipt_log_from_upload(uploaded_file)
        source_label = uploaded_file.name
        summary = summarize_logs(receipts)
    elif path_text.strip():
        path = Path(path_text.strip()).expanduser()
        receipts = _load_jsonl(path)
        source_label = str(path)
        summary = summarize_logs(path)
    else:
        summary = summarize_logs([])
except (OSError, json.JSONDecodeError, ValueError) as exc:
    st.error(f"Could not load receipt log: {exc}")
    _show_log_help()
    st.stop()

if not receipts:
    _show_log_help()
    st.stop()

st.subheader(f"Summary for {source_label}")

remaining = _remaining_budget(receipts)
col1, col2, col3 = st.columns(3)
col1.metric("Total cost", f"${summary['total_cost']:.4f}")
col2.metric("Actions", summary["number_of_actions"])
col3.metric("Remaining budget", "Not logged" if remaining is None else f"${remaining:.4f}")

st.subheader("AI vs Modeling Cost")
cost_split = _ai_vs_modeling_cost(receipts)
col1, col2, col3, col4 = st.columns(4)
col1.metric("AI / LLM usage", f"${cost_split['ai_cost']:.2f}")
col2.metric("Modeling cost", f"${cost_split['modeling_cost']:.2f}")
col3.metric("Other compute cost", f"${cost_split['other_compute_cost']:.2f}")
col4.metric("AI share of total", f"{cost_split['ai_share']:.0%}")
if cost_split["ai_cost"] > cost_split["modeling_cost"]:
    st.write("You spent more on AI assistance than on model training.")
else:
    st.write("AI assistance was a smaller portion of your total compute cost.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Cost by Category")
    st.bar_chart(summary["cost_by_category"])

with col2:
    st.subheader("Cost by Model")
    st.bar_chart(summary["cost_by_model"])

st.subheader("Most Expensive Action")
most_expensive = summary["most_expensive_action"]
if most_expensive:
    st.json(most_expensive)
else:
    st.write("No receipts found.")

st.subheader("Receipt Table")
st.dataframe(receipts, use_container_width=True)
