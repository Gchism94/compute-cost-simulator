from ccs import Budget, compute_block


def test_compute_block_adds_receipt(tmp_path):
    budget = Budget(total=1.0)
    log_path = tmp_path / "receipts.jsonl"
    config = {"runtime": {"cpu_second": 0.0}, "llm": {}}
    with compute_block(
        "test block",
        budget=budget,
        config=config,
        log_path=log_path,
    ):
        pass
    assert len(budget.receipts) == 1
    assert budget.receipts[0]["runtime_seconds"] >= 0
    assert budget.receipts[0]["cost"] == 0.0
    assert log_path.exists()


def test_compute_block_checks_estimated_cost_when_budget_enforced():
    budget = Budget(total=1.0, enforce=True)
    config = {"runtime": {"cpu_second": 0.0}, "llm": {}}

    with compute_block(
        "affordable block",
        budget=budget,
        estimated_cost=0.5,
        config=config,
    ):
        pass

    assert len(budget.receipts) == 1
