import pytest

from ccs import Budget
from ccs.cost_model import (
    can_afford,
    estimate_action_cost,
    estimate_batch_cost,
    estimate_llm_cost,
    estimate_runtime_cost,
)


def test_runtime_cost_cpu_only():
    config = {"runtime": {"cpu_second": 0.1}, "llm": {}}
    assert estimate_runtime_cost(runtime_seconds=10, config=config) == 1.0


def test_llm_cost():
    config = {"runtime": {}, "llm": {"small": {"input_token": 0.1, "output_token": 0.2}}}
    assert estimate_llm_cost("small", input_tokens=10, output_tokens=5, config=config) == 2.0


def test_llm_cost_unknown_model_size():
    with pytest.raises(ValueError, match="Expected one of"):
        estimate_llm_cost("huge", input_tokens=10, output_tokens=5)


def test_estimate_action_cost_combines_runtime_and_llm_cost():
    config = {
        "runtime": {"cpu_second": 0.1, "gpu_second": 0.2},
        "llm": {"small": {"input_token": 0.01, "output_token": 0.02}},
    }

    cost = estimate_action_cost(
        runtime_seconds=10,
        gpu_used=True,
        model_size="small",
        input_tokens=100,
        output_tokens=50,
        config=config,
    )

    assert cost == 5.0


def test_estimate_batch_cost():
    assert estimate_batch_cost(cost_per_action=0.25, n_actions=4) == 1.0


def test_can_afford():
    budget = Budget(total=1.0)
    budget.add_receipt({"task": "first action", "cost": 0.25})

    assert can_afford(budget, estimated_cost=0.75) is True
    assert can_afford(budget, estimated_cost=0.76) is False
