from ccs import Budget, CostModel, compute_block


def test_compute_block_adds_receipt(tmp_path):
    budget = Budget(total=1.0)
    model = CostModel(costs={"cpu_second": 0.0}, llm_models={})
    with compute_block(
        "test block",
        budget=budget,
        cost_model=model,
        log=True,
        log_dir=tmp_path,
    ):
        pass
    assert len(budget.receipts) == 1
    assert (tmp_path / "receipts.jsonl").exists()
    assert (tmp_path / "receipts.csv").exists()
