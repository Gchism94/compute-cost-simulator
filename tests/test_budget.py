import pytest

from ccs import Budget, BudgetExceededError


def test_budget_tracks_spending():
    budget = Budget(total=1.0)
    budget.add_receipt({"task": "a", "cost": 0.25})
    assert budget.spent == 0.25
    assert budget.remaining() == 0.75
    assert budget.percent_spent() == 0.25
    assert budget.is_over_budget() is False
    assert budget.summary()["number_of_actions"] == 1


def test_budget_enforcement_off_does_not_raise():
    budget = Budget(total=1.0, enforce=False)

    assert budget.check_affordable(estimated_cost=2.0) is True


def test_budget_enforcement_raises_when_estimate_exceeds_remaining():
    budget = Budget(total=1.0, enforce=True)
    budget.add_receipt({"task": "first action", "cost": 0.75})

    with pytest.raises(BudgetExceededError, match="estimated cost \\$0.26"):
        budget.check_affordable(estimated_cost=0.26)


def test_budget_enforcement_allows_affordable_actions():
    budget = Budget(total=1.0, enforce=True)

    assert budget.check_affordable(estimated_cost=0.25) is True
