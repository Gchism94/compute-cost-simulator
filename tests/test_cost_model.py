from ccs import CostModel


def test_runtime_cost_cpu_only():
    model = CostModel(costs={"cpu_second": 0.1}, llm_models={})
    assert model.compute_runtime_cost(runtime_seconds=10) == 1.0


def test_llm_cost():
    model = CostModel(
        costs={},
        llm_models={"small": {"input_token": 0.1, "output_token": 0.2}},
    )
    assert model.compute_llm_cost("small", input_tokens=10, output_tokens=5) == 2.0
