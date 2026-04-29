import pytest

from ccs.cost_model import estimate_llm_cost, estimate_runtime_cost


def test_runtime_cost_cpu_only():
    config = {"runtime": {"cpu_second": 0.1}, "llm": {}}
    assert estimate_runtime_cost(runtime_seconds=10, config=config) == 1.0


def test_llm_cost():
    config = {"runtime": {}, "llm": {"small": {"input_token": 0.1, "output_token": 0.2}}}
    assert estimate_llm_cost("small", input_tokens=10, output_tokens=5, config=config) == 2.0


def test_llm_cost_unknown_model_size():
    with pytest.raises(ValueError, match="Expected one of"):
        estimate_llm_cost("huge", input_tokens=10, output_tokens=5)
