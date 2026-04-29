"""Minimal demo for runtime-based simulated costs."""

from time import sleep

from ccs import Budget, compute_block

budget = Budget(total=5.00)

with compute_block(
    task="train logistic regression",
    category="modeling",
    model="logistic_regression",
    budget=budget,
    metric_name="f1",
    metric_value=0.64,
):
    sleep(0.25)

with compute_block(
    task="train random forest",
    category="modeling",
    model="random_forest",
    budget=budget,
    metric_name="f1",
    metric_value=0.68,
):
    sleep(0.75)

print(budget.summary())
