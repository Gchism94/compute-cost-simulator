# Roadmap

This roadmap separates the current prototype from curriculum expansion and
future software features. All cost values remain simulated unless a future
version explicitly introduces optional real-price integrations.

## Current Prototype

- Lightweight Python package with no required runtime dependencies.
- Public API:
  - `Budget`
  - `compute_block`
  - `track_llm_call`
  - `load_cost_config`
  - `summarize_logs`
- Student-facing examples for modeling, LLM token costs, hyperparameter search,
  inference scaling, RAG, vibe coding, and budget failure.
- Optional Streamlit dashboard prototype for JSONL receipt logs.
- Teaching materials for assignments, reflection, rubrics, and discussion.

## Curriculum Expansion

- Add instructor notes for each of the seven curriculum modules.
- Add short worksheets for pre-run estimation.
- Add sample student responses and model answers.
- Add alternative budget settings for short labs, homework, and final projects.
- Add more examples connecting cost-aware computing to reproducibility,
  accessibility, and institutional resource constraints.
- Add optional notebooks only after the command-line examples are stable.

## Future Software Features

- Improve JSONL and CSV export examples.
- Add more tests for config loading, budget export, and exception paths.
- Add optional dashboard filters by category, model, and date.
- Add configurable course profiles for different teaching scenarios.
- Add richer summaries for marginal cost, cost per metric, and repeated-run projections.
- Consider optional real-price reference profiles only if they remain clearly
  separate from the simulated pedagogical defaults.

## Not Planned For The Core Prototype

- Required dashboards.
- Required pandas, numpy, scikit-learn, plotting, or web framework dependencies.
- Real cloud billing integrations in the default package.
- Automatic enforcement that blocks execution when budgets are exceeded.
