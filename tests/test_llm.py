from ccs import Budget, track_llm_call


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
