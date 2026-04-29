# Compute Cost Simulator Context

This repository is a lightweight Python package for teaching cost-aware computing.

The package should help students understand simulated computational costs for:
- CPU time
- GPU time
- storage
- memory
- LLM token usage

All costs are simulated pedagogical estimates, not real billing.

Design priorities:
- readable student-facing code
- minimal dependencies
- notebook-friendly API
- simple receipts
- budget tracking
- reflection on performance vs. cost

Public API:
- Budget
- compute_block
- track_llm_call
- load_cost_config
- summarize_logs

Avoid dashboards, cloud APIs, or heavy dependencies unless the task explicitly asks for them.