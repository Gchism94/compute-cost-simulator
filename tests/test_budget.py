from ccs import Budget


def test_budget_tracks_spending():
    budget = Budget(total=1.0)
    budget.add_receipt({"task": "a", "cost": 0.25})
    assert budget.spent == 0.25
    assert budget.remaining() == 0.75
    assert budget.percent_spent() == 0.25
    assert budget.is_over_budget() is False
    assert budget.summary()["number_of_actions"] == 1
