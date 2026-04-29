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


st.set_page_config(page_title="Compute Cost Simulator", layout="wide")
st.title("Compute Cost Simulator Dashboard")
st.caption("All costs shown here are simulated pedagogical estimates, not real billing.")

with st.sidebar:
    st.header("Receipt Log")
    uploaded_file = st.file_uploader("Upload JSONL receipt log", type=["jsonl"])
    path_text = st.text_input("Or enter a JSONL path", value="")

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
    st.stop()

if not receipts:
    st.info("Upload a JSONL receipt log or enter a path to get started.")
    st.stop()

st.subheader(f"Summary for {source_label}")

remaining = _remaining_budget(receipts)
col1, col2, col3 = st.columns(3)
col1.metric("Total cost", f"${summary['total_cost']:.4f}")
col2.metric("Actions", summary["number_of_actions"])
col3.metric("Remaining budget", "Not logged" if remaining is None else f"${remaining:.4f}")

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
