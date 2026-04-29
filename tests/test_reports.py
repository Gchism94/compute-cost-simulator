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
