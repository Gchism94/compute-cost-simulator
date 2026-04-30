import pytest

from ccs import Budget, BudgetExceededError, track_llm_call


def test_track_llm_call_creates_receipt_and_jsonl_log(tmp_path):
    budget = Budget(total=1.0)
    log_path = tmp_path / "receipts.jsonl"

    receipt = track_llm_call(
        task="summarize note",
        model_size="small",
        input_tokens=100,
        output_tokens=25,
        budget=budget,
        log_path=log_path,
    )

    assert receipt["total_tokens"] == 125
    assert receipt in budget.receipts
    assert log_path.read_text(encoding="utf-8").strip()


def test_track_llm_call_checks_estimated_cost_when_budget_enforced():
    budget = Budget(total=0.01, enforce=True)

    with pytest.raises(BudgetExceededError):
        track_llm_call(
            task="large request",
            model_size="large",
            input_tokens=100,
            output_tokens=25,
            budget=budget,
            estimated_cost=0.02,
        )

    assert budget.receipts == []
