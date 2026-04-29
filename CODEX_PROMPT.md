# Codex prompt

You are working on the Compute Cost Simulator, a lightweight Python package for teaching cost-aware computing.

## Goal

Extend this scaffold into a usable prototype for Jupyter notebooks. Keep the package simple, readable, and pedagogical.

## Immediate tasks

1. Review the existing API:
   - `Budget`
   - `CostModel`
   - `compute_block()`
   - `track_llm_call()`
2. Improve receipt logging so JSON and CSV schemas are stable across runs.
3. Add a `Budget.to_dataframe()` method if pandas is installed, but do not require pandas as a dependency.
4. Add notebook-friendly display helpers.
5. Add stronger report functions:
   - total spent
   - remaining budget
   - most expensive action
   - cost by category
   - cost by model
   - cost per metric when available
6. Add tests for edge cases:
   - over-budget actions
   - unknown LLM model sizes
   - GPU vs CPU cost differences
   - zero or missing metric values
7. Add a simple markdown assignment template in `examples/assignment_prompt.md`.

## Design constraints

- No real cloud billing APIs.
- No cloud credentials.
- Costs are simulated pedagogical estimates.
- Keep the public API beginner-friendly.
- Prefer standard library tools unless an external dependency is clearly useful.
- Maintain compatibility with Python 3.10+.
