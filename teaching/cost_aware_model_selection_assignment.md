# Cost-Aware Model Selection Challenge

## Overview

In this assignment, you will compare computational approaches under a simulated
compute budget. Your final choice should be justified using performance, cost,
scalability, and reproducibility.

All costs in this assignment are simulated pedagogical estimates. They are not
real billing charges.

## Learning Goals

By the end of this assignment, you should be able to:

- Explain that compute has cost, even when the cost is hidden from you.
- Compare model performance and simulated compute cost.
- Identify when an expensive model is not justified by its performance gain.
- Estimate how costs change at classroom or project scale.
- Reflect on how generative AI tool usage affects total cost.

## Setup

Install the package from the repository root:

```bash
pip install -e .
```

Run the flagship demo:

```bash
python examples/flagship_budget_failure_demo.py
```

Optional: run the realistic scenario comparison demo:

```bash
python examples/realistic_usage_scenarios_demo.py
```

## Student Task

Choose a fixed simulated compute budget, such as `$0.20`, `$1.00`, or another
amount assigned by your instructor. Then complete a small model selection or
workflow comparison.

Your work must include:

- At least three approaches.
- At least one cheap baseline.
- At least one more expensive approach.
- CCS receipts for all major actions.
- A performance or usefulness metric for each approach.
- A final recommendation that uses both performance and cost evidence.

Your approaches may be real code, simulated runs with `time.sleep()`, LLM calls,
RAG-style workflows, AI-assisted coding steps, or a combination of these.

## Required Analysis

For each approach, report:

- Model or workflow name.
- Performance metric, such as F1, accuracy, quality score, or usefulness score.
- Simulated cost.
- Cost per metric, if appropriate.
- Whether the result was worth the cost.

Also include one short scale estimate:

- What would this workflow cost if 40 students each ran it once?
- What would it cost if each student repeated it 5 times?
- Would your final workflow still be reasonable at that scale?

## GenAI Usage Statement

Generative AI tools are allowed if your instructor permits them, but you must be
transparent about how you used them.

Include a GenAI Usage Statement with:

- Tools used.
- Approximate number of interactions or major chat turns.
- What you used AI for.
- One AI suggestion you accepted.
- One AI suggestion you rejected.
- The approximate AI cost tracked by CCS, if you used `track_llm_call()`.

If you did not use generative AI, write:

> I did not use generative AI support for this assignment.

## Manual Requirement

At least one model or workflow decision must be made without AI-generated code.

In your submission, identify that decision and explain your reasoning in your
own words. This can be a choice to run a smaller model, skip an expensive search,
reduce token usage, choose a baseline, or select a final model.

## Reflection Questions

Answer these questions in direct, specific language:

1. What was your starting budget?
2. Which approach was cheapest?
3. Which approach performed best?
4. Did the best-performing approach justify its extra cost?
5. What did you estimate before running it?
6. Did any estimate change your plan?
7. Which action or workflow cost the most?
8. How did AI tool usage affect your total cost, if you used AI?
9. Could another student reproduce your final workflow under the same budget?
10. What is your final recommendation, and why?

## Submission Checklist

Submit:

- Receipt log or receipt summary.
- Short written justification.
- Budget summary.
- Final model or workflow choice.
- GenAI Usage Statement.
- Answers to the reflection questions.

## Rubric

Total: 100 points

## Cost Tracking: 20 Points

- 20: Tracks all major actions with clear CCS receipts.
- 15: Tracks most actions with minor omissions.
- 10: Tracks some actions but leaves out important costs.
- 5: Mentions cost without enough receipt evidence.
- 0: Does not address cost.

## Model Comparison: 20 Points

- 20: Compares at least three approaches using performance and cost.
- 15: Compares three approaches but misses some cost-performance detail.
- 10: Compares fewer than three approaches or reports results unevenly.
- 5: Describes approaches without meaningful comparison.
- 0: Does not compare approaches.

## Budget Reasoning: 20 Points

- 20: Uses budget limits and estimates to explain what was run, skipped, or reduced.
- 15: Discusses budget limits but does not fully connect them to decisions.
- 10: Mentions budget after the fact with limited reasoning.
- 5: Gives vague budget comments.
- 0: Does not reason about the budget.

## Scalability And Reproducibility: 15 Points

- 15: Estimates classroom or repeated-project cost and explains reproducibility.
- 12: Addresses scale or reproducibility well, but not both.
- 8: Mentions scale or reproducibility briefly.
- 4: Gives an unclear or unsupported scale estimate.
- 0: Does not address scale or reproducibility.

## AI Transparency: 15 Points

- 15: Clearly reports AI use, tracks AI-related cost when applicable, and explains personal decisions.
- 12: Reports AI use but needs more detail about cost or decision-making.
- 8: Mentions AI use without enough transparency.
- 4: AI use is unclear or appears to replace your own reasoning.
- 0: Does not disclose AI use when AI appears to have been used.

## Clarity: 10 Points

- 10: Writing is clear, organized, and evidence-based.
- 8: Writing is mostly clear with minor gaps.
- 5: Writing is understandable but hard to follow.
- 2: Writing is vague or disorganized.
- 0: Submission is missing or not readable.
