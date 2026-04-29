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
        '  pip install "streamlit>=1.30"'
    ) from exc

from ccs import summarize_logs


DEFAULT_LOG_PATH = "logs/ccs_session.jsonl"
FLOAT_TOLERANCE = 1e-9
TABLE_COLUMNS = [
    "task",
    "category",
    "model",
    "cost",
    "runtime_seconds",
    "total_tokens",
    "metric_name",
    "metric_value",
    "budget_remaining_after",
]


def _currency(value: float | int | None) -> str:
    amount = float(value or 0.0)
    if 0 < abs(amount) < 0.01:
        return f"${amount:.4f}"
    return f"${amount:.2f}"


def _percent(value: float) -> str:
    return f"{value:.0%}"


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                receipts.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc.msg}") from exc
    return receipts


def _receipt_log_from_upload(uploaded_file: Any) -> list[dict[str, Any]]:
    receipts: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(
        uploaded_file.getvalue().decode("utf-8").splitlines(),
        start=1,
    ):
        if not raw_line.strip():
            continue
        try:
            receipts.append(json.loads(raw_line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on uploaded line {line_number}: {exc.msg}") from exc
    return receipts


def _latest_budget_status(receipts: list[dict[str, Any]]) -> dict[str, float] | None:
    for receipt in reversed(receipts):
        if "budget_total" not in receipt:
            continue

        budget_total = float(receipt["budget_total"])
        spent = float(receipt.get("budget_spent_after", 0.0))
        if not spent:
            spent = budget_total - float(receipt.get("budget_remaining_after", budget_total))

        remaining = float(receipt.get("budget_remaining_after", budget_total - spent))
        percent_spent = spent / budget_total if budget_total else 0.0
        return {
            "budget_total": budget_total,
            "spent": spent,
            "remaining": remaining,
            "percent_spent": percent_spent,
        }
    return None


def _risk_label(percent_spent: float) -> str:
    if percent_spent > 1:
        return "Over budget"
    if percent_spent >= 0.8:
        return "High"
    if percent_spent >= 0.5:
        return "Medium"
    return "Low"


def _ai_vs_modeling_cost(receipts: list[dict[str, Any]]) -> dict[str, float]:
    total_cost = sum(float(receipt.get("cost", 0.0)) for receipt in receipts)
    ai_cost = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if receipt.get("category") in {"llm", "ai_support"}
    )
    modeling_cost = sum(
        float(receipt.get("cost", 0.0))
        for receipt in receipts
        if receipt.get("category") == "modeling"
    )
    other_cost = total_cost - ai_cost - modeling_cost
    if -FLOAT_TOLERANCE < other_cost < 0:
        other_cost = 0.0
    ai_share = ai_cost / total_cost if total_cost else 0.0
    return {
        "total_cost": total_cost,
        "ai_cost": ai_cost,
        "modeling_cost": modeling_cost,
        "other_cost": other_cost,
        "ai_share": ai_share,
    }


def _burn_rows(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cumulative_cost = 0.0
    for index, receipt in enumerate(receipts, start=1):
        cost = float(receipt.get("cost", 0.0))
        cumulative_cost += cost
        rows.append(
            {
                "action": index,
                "task": receipt.get("task", ""),
                "category": receipt.get("category", ""),
                "model": receipt.get("model", ""),
                "cost": round(cost, 6),
                "cumulative_cost": round(cumulative_cost, 6),
                "remaining_budget": receipt.get("budget_remaining_after"),
            }
        )
    return rows


def _chart_data(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    data = {
        "cost_per_action": [float(row["cost"]) for row in rows],
        "cumulative_cost": [float(row["cumulative_cost"]) for row in rows],
    }
    remaining = [row.get("remaining_budget") for row in rows]
    if any(value is not None for value in remaining):
        data["remaining_budget"] = [
            float(value) if value is not None else 0.0 for value in remaining
        ]
    return data


def _clean_receipt_table(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_columns = sorted({key for receipt in receipts for key in receipt})
    ordered_columns = TABLE_COLUMNS + [col for col in all_columns if col not in TABLE_COLUMNS]
    return [{col: receipt.get(col) for col in ordered_columns if col in receipt} for receipt in receipts]


def _show_log_help() -> None:
    st.info(
        "No receipts loaded yet. To generate a dashboard log:\n\n"
        "1. Run `python examples/flagship_budget_failure_demo.py`\n"
        "2. Run additional examples if desired\n"
        f"3. Load `{DEFAULT_LOG_PATH}`"
    )


st.set_page_config(page_title="Compute Cost Simulator", layout="wide")
st.title("Compute Cost Simulator")
st.caption("Simulated compute costs for teaching cost-aware AI and data science.")

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
    elif path_text.strip():
        path = Path(path_text.strip()).expanduser()
        receipts = _load_jsonl(path)
        source_label = str(path)
except (OSError, ValueError) as exc:
    st.error(f"Could not load receipt log: {exc}")
    _show_log_help()
    st.stop()

if not receipts:
    _show_log_help()
    st.stop()

summary = summarize_logs(receipts)
budget_status = _latest_budget_status(receipts)
cost_split = _ai_vs_modeling_cost(receipts)
burn_rows = _burn_rows(receipts)
receipt_table = _clean_receipt_table(receipts)
most_expensive = summary["most_expensive_action"]

st.write(f"Loaded `{source_label}` with {summary['number_of_actions']} receipts.")

overview_tab, breakdown_tab, burn_tab, receipt_tab = st.tabs(
    ["Overview", "Cost Breakdown", "Budget Burn", "Receipt Log"]
)

with overview_tab:
    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total cost", _currency(summary["total_cost"]))
    col2.metric("Actions", summary["number_of_actions"])
    if budget_status:
        col3.metric("Remaining budget", _currency(budget_status["remaining"]))
    else:
        col3.metric("Remaining budget", "Not logged")

    st.subheader("Budget Risk Meter")
    if budget_status:
        percent_spent = budget_status["percent_spent"]
        risk = _risk_label(percent_spent)
        st.progress(min(max(percent_spent, 0.0), 1.0))
        cols = st.columns(4)
        cols[0].metric("Budget", _currency(budget_status["budget_total"]))
        cols[1].metric("Spent", _currency(budget_status["spent"]))
        cols[2].metric("Percent spent", _percent(percent_spent))
        cols[3].metric("Risk level", risk)
        if risk == "Over budget":
            st.warning("Your workflow has exceeded the logged budget.")
        elif risk == "High":
            st.warning("Your workflow is close to the budget limit.")
        elif risk == "Medium":
            st.info("Your workflow has used a noticeable share of the budget.")
        else:
            st.success("Your workflow is currently at low budget risk.")
    else:
        st.info("No budget fields were found in this log.")

    st.subheader("AI vs Modeling Cost")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AI / LLM usage", _currency(cost_split["ai_cost"]))
    col2.metric("Modeling cost", _currency(cost_split["modeling_cost"]))
    col3.metric("Other compute cost", _currency(cost_split["other_cost"]))
    col4.metric("AI share of total", _percent(cost_split["ai_share"]))
    if cost_split["ai_cost"] + cost_split["modeling_cost"] > cost_split["total_cost"] + FLOAT_TOLERANCE:
        st.warning("Cost split check: AI plus modeling cost exceeds total cost.")
    if cost_split["ai_cost"] > cost_split["modeling_cost"]:
        st.warning("You spent more on AI assistance than on model training.")
    else:
        st.success("AI assistance was a smaller portion of your total compute cost.")

    st.subheader("Classroom Projection")
    col1, col2, col3 = st.columns(3)
    students = col1.number_input("Number of students", min_value=1, value=40, step=1)
    runs_per_student = col2.number_input("Runs per student", min_value=1, value=5, step=1)
    projected_total = cost_split["total_cost"] * students * runs_per_student
    col3.metric("Projected total cost", _currency(projected_total))
    st.info("Small individual costs can become large when repeated across a class.")

with breakdown_tab:
    st.subheader("Cost by Category")
    st.bar_chart(summary["cost_by_category"])

    st.subheader("Cost by Model")
    st.bar_chart(summary["cost_by_model"])

    st.subheader("Most Expensive Action")
    if most_expensive:
        st.write(
            f"`{most_expensive.get('task', 'unknown task')}` cost "
            f"{_currency(float(most_expensive.get('cost', 0.0)))}."
        )
    else:
        st.info("No receipts found.")

with burn_tab:
    st.subheader("Budget Burn Over Time")
    st.info("This chart shows where your budget started to disappear.")
    st.line_chart(_chart_data(burn_rows))

    st.subheader("Receipt Timeline")
    st.dataframe(burn_rows, use_container_width=True)

with receipt_tab:
    st.subheader("Full Receipt Table")
    st.dataframe(receipt_table, use_container_width=True)

    st.subheader("Raw Most Expensive Receipt")
    if most_expensive:
        with st.expander("Show raw JSON"):
            st.json(most_expensive)
    else:
        st.info("No receipts found.")
