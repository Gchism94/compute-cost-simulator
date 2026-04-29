from ccs import summarize_logs


def test_summarize_logs_groups_by_category():
    summary = summarize_logs(
        [
            {"task": "a", "category": "modeling", "model": "small", "cost": 0.25},
            {"task": "b", "category": "modeling", "model": "large", "cost": 0.75},
            {"task": "c", "category": "llm", "model": "medium", "cost": 0.50},
        ]
    )

    assert summary["total_cost"] == 1.5
    assert summary["number_of_actions"] == 3
    assert summary["cost_by_category"] == {"modeling": 1.0, "llm": 0.5}
    assert summary["cost_by_model"]["large"] == 0.75


def test_summarize_logs_accepts_jsonl_path(tmp_path):
    log_path = tmp_path / "receipts.jsonl"
    log_path.write_text(
        '{"task": "a", "category": "modeling", "model": "small", "cost": 0.25}\n'
        '{"task": "b", "category": "llm", "model": "medium", "cost": 0.50}\n',
        encoding="utf-8",
    )

    summary = summarize_logs(log_path)

    assert summary["total_cost"] == 0.75
    assert summary["average_cost"] == 0.375
