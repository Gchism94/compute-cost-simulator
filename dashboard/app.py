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
HIDDEN_BY_DEFAULT = {
    "memory_gb_seconds",
    "storage_mb",
    "timestamp",
    "budget_total",
    "budget_spent_after",
    "budget_warning",
    "over_budget",
}
SPECIAL_LABELS = {
    "runtime_seconds": "Runtime (Seconds)",
    "total_tokens": "Total Tokens",
    "metric_name": "Metric",
    "metric_value": "Metric Value",
    "cost_per_metric": "Cost per Metric",
    "budget_remaining_after": "Remaining Budget",
    "model_size": "Model Size",
    "llm": "LLM",
    "gpu": "GPU",
    "cpu": "CPU",
    "ai": "AI",
    "rag": "RAG",
    "f1": "F1",
}


def format_label(name: str) -> str:
    cleaned = str(name).strip()
    lowered = cleaned.lower()
    if lowered in SPECIAL_LABELS:
        return SPECIAL_LABELS[lowered]

    words = cleaned.replace("_", " ").split()
    formatted_words = []
    for word in words:
        acronym = SPECIAL_LABELS.get(word.lower())
        formatted_words.append(acronym if acronym else word.title())
    return " ".join(formatted_words)


def format_currency(value: float | int | None) -> str:
    amount = float(value or 0.0)
    if abs(amount) < 1:
        return f"${amount:.4f}"
    return f"${amount:,.2f}"


def _percent(value: float) -> str:
    return f"{value:.0%}"


def _format_number(value: Any, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{float(value):,.{digits}f}"


def _format_integer(value: Any) -> str:
    if value is None:
        return "—"
    return f"{int(value):,}"


def _format_display_value(key: str, value: Any) -> str:
    if value is None:
        return "—"
    if key in {"cost", "cost_per_metric", "budget_remaining_after", "budget_total", "budget_spent_after"}:
        return format_currency(float(value))
    if key == "runtime_seconds":
        return _format_number(value, digits=3)
    if key == "metric_value":
        return _format_number(value, digits=2)
    if key == "total_tokens":
        return _format_integer(value)
    if key in {"category", "model", "model_size", "metric_name"}:
        return format_label(str(value))
    return str(value)


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
        "Cost per Action": [float(row["cost"]) for row in rows],
        "Cumulative Cost": [float(row["cumulative_cost"]) for row in rows],
    }
    remaining = [row.get("remaining_budget") for row in rows]
    if any(value is not None for value in remaining):
        data["Remaining Budget"] = [
            float(value) if value is not None else 0.0 for value in remaining
        ]
    return data


def _display_receipt_table(
    receipts: list[dict[str, Any]],
    include_hidden: bool = False,
) -> list[dict[str, Any]]:
    all_columns = sorted({key for receipt in receipts for key in receipt})
    extra_columns = [
        col
        for col in all_columns
        if col not in TABLE_COLUMNS and (include_hidden or col not in HIDDEN_BY_DEFAULT)
    ]
    ordered_columns = TABLE_COLUMNS + extra_columns
    rows: list[dict[str, Any]] = []
    for receipt in receipts:
        row = {}
        for column in ordered_columns:
            if column in receipt:
                row[format_label(column)] = _format_display_value(column, receipt[column])
        rows.append(row)
    return rows


def _display_burn_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    displayed_rows: list[dict[str, Any]] = []
    for row in rows:
        displayed_rows.append(
            {
                "Action": row["action"],
                "Task": row["task"],
                "Category": format_label(str(row["category"])),
                "Model": format_label(str(row["model"])),
                "Cost": format_currency(row["cost"]),
                "Cumulative Cost": format_currency(row["cumulative_cost"]),
                "Remaining Budget": (
                    format_currency(float(row["remaining_budget"]))
                    if row.get("remaining_budget") is not None
                    else "—"
                ),
            }
        )
    return displayed_rows


def _format_cost_totals(costs: dict[str, float]) -> dict[str, float]:
    return {format_label(key): value for key, value in costs.items()}


def _scenario_rows(receipts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scenarios = sorted({str(receipt["scenario"]) for receipt in receipts if receipt.get("scenario")})
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        scenario_receipts = [receipt for receipt in receipts if receipt.get("scenario") == scenario]
        split = _ai_vs_modeling_cost(scenario_receipts)
        rows.append(
            {
                "Scenario": scenario,
                "Total Cost": split["total_cost"],
                "AI / LLM Cost": split["ai_cost"],
                "Modeling Cost": split["modeling_cost"],
                "Action Count": len(scenario_receipts),
                "AI Share": split["ai_share"],
                "Projected Classroom Cost": split["total_cost"] * 40,
                "Projected 5x Project Cost": split["total_cost"] * 40 * 5,
            }
        )
    return rows


def _display_scenario_rows(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    displayed_rows: list[dict[str, str]] = []
    for row in rows:
        displayed_rows.append(
            {
                "Scenario": row["Scenario"],
                "Total Cost": format_currency(row["Total Cost"]),
                "AI / LLM Cost": format_currency(row["AI / LLM Cost"]),
                "Modeling Cost": format_currency(row["Modeling Cost"]),
                "Action Count": _format_integer(row["Action Count"]),
                "AI Share": _percent(row["AI Share"]),
                "Projected Classroom Cost": format_currency(row["Projected Classroom Cost"]),
                "Projected 5x Project Cost": format_currency(row["Projected 5x Project Cost"]),
            }
        )
    return displayed_rows


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
receipt_table = _display_receipt_table(receipts)
full_receipt_table = _display_receipt_table(receipts, include_hidden=True)
most_expensive = summary["most_expensive_action"]
scenario_rows = _scenario_rows(receipts)

st.write(f"Loaded `{source_label}` with {summary['number_of_actions']} receipts.")

overview_tab, breakdown_tab, burn_tab, scenario_tab, receipt_tab = st.tabs(
    ["Overview", "Cost Breakdown", "Budget Burn", "Scenario Comparison", "Receipt Log"]
)

with overview_tab:
    st.subheader("Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cost", format_currency(summary["total_cost"]))
    col2.metric("Actions", summary["number_of_actions"])
    if budget_status:
        col3.metric("Remaining Budget", format_currency(budget_status["remaining"]))
    else:
        col3.metric("Remaining Budget", "Not Logged")

    st.subheader("Budget Risk Meter")
    if budget_status:
        percent_spent = budget_status["percent_spent"]
        risk = _risk_label(percent_spent)
        st.progress(min(max(percent_spent, 0.0), 1.0))
        cols = st.columns(4)
        cols[0].metric("Budget", format_currency(budget_status["budget_total"]))
        cols[1].metric("Spent", format_currency(budget_status["spent"]))
        cols[2].metric("Percent Spent", _percent(percent_spent))
        cols[3].metric("Risk Level", risk)
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
    col1.metric("AI / LLM Usage", format_currency(cost_split["ai_cost"]))
    col2.metric("Modeling Cost", format_currency(cost_split["modeling_cost"]))
    col3.metric("Other Compute Cost", format_currency(cost_split["other_cost"]))
    col4.metric("AI Share of Total", _percent(cost_split["ai_share"]))
    if cost_split["ai_cost"] + cost_split["modeling_cost"] > cost_split["total_cost"] + FLOAT_TOLERANCE:
        st.warning("Cost split check: AI plus modeling cost exceeds total cost.")
    if cost_split["ai_cost"] > cost_split["modeling_cost"]:
        st.warning("You spent more on AI assistance than on model training.")
    else:
        st.success("AI assistance was a smaller portion of your total compute cost.")

    st.subheader("Classroom Projection")
    col1, col2, col3 = st.columns(3)
    students = col1.number_input("Number of Students", min_value=1, value=40, step=1)
    runs_per_student = col2.number_input("Runs per Student", min_value=1, value=5, step=1)
    projected_total = cost_split["total_cost"] * students * runs_per_student
    col3.metric("Projected Total Cost", format_currency(projected_total))
    st.info("Small individual costs can become large when repeated across a class.")

with breakdown_tab:
    st.subheader("Cost by Category")
    st.bar_chart(_format_cost_totals(summary["cost_by_category"]))

    st.subheader("Cost by Model")
    st.bar_chart(_format_cost_totals(summary["cost_by_model"]))

    st.subheader("Most Expensive Action")
    if most_expensive:
        st.write(
            f"`{most_expensive.get('task', 'unknown task')}` cost "
            f"{format_currency(float(most_expensive.get('cost', 0.0)))}."
        )
    else:
        st.info("No receipts found.")

with burn_tab:
    st.subheader("Budget Burn Over Time")
    st.info("This chart shows where your budget started to disappear.")
    st.caption("X-axis: Action order. Y-axis: Simulated cost.")
    st.line_chart(_chart_data(burn_rows))

    st.subheader("Receipt Timeline")
    st.dataframe(_display_burn_table(burn_rows), width="stretch")

with scenario_tab:
    st.subheader("Scenario Comparison")
    if not scenario_rows:
        st.info(
            "Run `python examples/realistic_usage_scenarios_demo.py` to generate scenario logs."
        )
    else:
        st.write(
            "Use this tab to compare structured classroom work with more open-ended "
            "project workflows."
        )
        st.dataframe(_display_scenario_rows(scenario_rows), width="stretch")

        st.subheader("Total Cost by Scenario")
        st.bar_chart({row["Scenario"]: row["Total Cost"] for row in scenario_rows})

        st.subheader("AI / LLM Cost by Scenario")
        st.bar_chart({row["Scenario"]: row["AI / LLM Cost"] for row in scenario_rows})

        st.subheader("Modeling Cost by Scenario")
        st.bar_chart({row["Scenario"]: row["Modeling Cost"] for row in scenario_rows})

        st.subheader("Classroom vs Outside-Class Projection")
        col1, col2, col3, col4 = st.columns(4)
        students = col1.number_input("Students", min_value=1, value=40, step=1)
        repetitions = col2.number_input("Repetitions per Student", min_value=1, value=5, step=1)
        in_class_sessions = col3.number_input("In-Class Sessions per Term", min_value=1, value=6, step=1)
        project_iterations = col4.number_input("Project Iterations per Student", min_value=1, value=10, step=1)

        scenario_costs = {row["Scenario"]: float(row["Total Cost"]) for row in scenario_rows}
        structured_cost = scenario_costs.get("Structured In-Class Lab", 0.0)
        project_cost = scenario_costs.get("Student Project Workflow", 0.0)
        uninhibited_cost = scenario_costs.get("Uninhibited AI-Assisted Workflow", project_cost)

        structured_total = structured_cost * students * in_class_sessions
        project_total = project_cost * students * project_iterations
        uninhibited_total = uninhibited_cost * students * repetitions
        difference = uninhibited_total - structured_total

        metric_cols = st.columns(4)
        metric_cols[0].metric("Structured Classroom Total", format_currency(structured_total))
        metric_cols[1].metric("Project-Work Total", format_currency(project_total))
        metric_cols[2].metric("Uninhibited Workflow Total", format_currency(uninhibited_total))
        metric_cols[3].metric("Difference", format_currency(difference))

        st.info(
            "Classroom labs usually keep costs low by limiting model complexity, "
            "tokens, and repetitions. Project work can become more expensive "
            "because you try more models, ask for more AI help, paste longer "
            "context, and rerun workflows many times."
        )

with receipt_tab:
    st.subheader("Full Receipt Table")
    st.dataframe(receipt_table, width="stretch")

    with st.expander("Show Less Common Receipt Columns"):
        st.dataframe(full_receipt_table, width="stretch")

    st.subheader("Raw Most Expensive Receipt")
    if most_expensive:
        with st.expander("Show raw JSON"):
            st.json(most_expensive)
    else:
        st.info("No receipts found.")
