"""RAG cost burn demo: retrieval workflows have layered costs.

This example does not call a real embedding model, vector database, or LLM.
It uses CCS receipts to show why RAG costs include setup, retrieval, context,
and answer generation across repeated questions.
"""

import os
from time import sleep

from ccs import Budget, compute_block, track_llm_call


LOG_DIR = "logs"
LOG_PATH = os.path.join(LOG_DIR, "ccs_session.jsonl")
os.makedirs(LOG_DIR, exist_ok=True)


CLASSROOM_COST_CONFIG = {
    "runtime": {
        "cpu_second": 0.03,
        "gpu_second": 0.0,
        "memory_gb_second": 0.0,
        "storage_mb": 0.001,
    },
    "llm": {
        "small": {"input_token": 0.000004, "output_token": 0.0},
        "medium": {"input_token": 0.000012, "output_token": 0.00003},
    },
}


def dollars(value: float) -> str:
    return f"${value:.2f}"


def estimate_llm_cost(model_size: str, input_tokens: int, output_tokens: int) -> float:
    rates = CLASSROOM_COST_CONFIG["llm"][model_size]
    return round(
        input_tokens * rates["input_token"] + output_tokens * rates["output_token"],
        6,
    )


budget = Budget(total=0.80)

document_tokens = 24_000
chunk_count = 80
chunk_size_tokens = 300
questions = [
    {"label": "Q1", "top_k": 3, "question_tokens": 80, "history_tokens": 0, "answer_tokens": 220},
    {"label": "Q2", "top_k": 5, "question_tokens": 95, "history_tokens": 300, "answer_tokens": 260},
    {"label": "Q3", "top_k": 8, "question_tokens": 110, "history_tokens": 650, "answer_tokens": 320},
    {"label": "Q4", "top_k": 8, "question_tokens": 120, "history_tokens": 950, "answer_tokens": 360},
]

print("Compute Cost Simulator: RAG Cost Burn Demo")
print("===========================================")
print("RAG cost comes from several layers, not just the final chatbot answer.")

print("\nSetup")
print("-----")
sleep(0.02)
embedding_receipt = track_llm_call(
    task="embed course documents",
    model_size="small",
    input_tokens=document_tokens,
    output_tokens=0,
    budget=budget,
    category="rag_embedding",
    model="embedding_model",
    config=CLASSROOM_COST_CONFIG,
    log_path=LOG_PATH,
)

with compute_block(
    task="store and index document chunks",
    category="rag_indexing",
    model="vector_index",
    budget=budget,
    storage_mb=chunk_count * 0.25,
    config=CLASSROOM_COST_CONFIG,
    log_path=LOG_PATH,
):
    sleep(0.03)

index_receipt = budget.receipts[-1]
setup_cost = embedding_receipt["cost"] + index_receipt["cost"]
print(f"Embedded {document_tokens:,} document tokens: {dollars(embedding_receipt['cost'])}")
print(f"Stored/indexed {chunk_count} chunks: {dollars(index_receipt['cost'])}")
print(f"Upfront setup cost: {dollars(setup_cost)}")

print("\nQuestion costs")
print("--------------")
print(
    f"{'Q':>2} {'Top-k':>5} {'Context':>9} {'Input tok':>10} "
    f"{'Estimated':>10} {'Actual':>8} {'Cumulative':>11}"
)
print("-" * 72)

for question in questions:
    retrieved_context_tokens = question["top_k"] * chunk_size_tokens
    llm_input_tokens = (
        question["question_tokens"] + question["history_tokens"] + retrieved_context_tokens
    )
    estimated_generation_cost = estimate_llm_cost(
        "medium",
        input_tokens=llm_input_tokens,
        output_tokens=question["answer_tokens"],
    )

    with compute_block(
        task=f"retrieve context for {question['label']}",
        category="rag_retrieval",
        model=f"top_k={question['top_k']}",
        budget=budget,
        metric_name="chunks",
        metric_value=question["top_k"],
        config=CLASSROOM_COST_CONFIG,
        log_path=LOG_PATH,
    ):
        sleep(0.01)

    retrieval_receipt = budget.receipts[-1]
    sleep(0.02)
    llm_receipt = track_llm_call(
        task=f"answer {question['label']} with retrieved context",
        model_size="medium",
        input_tokens=llm_input_tokens,
        output_tokens=question["answer_tokens"],
        budget=budget,
        category="rag_generation",
        model="rag_chatbot",
        config=CLASSROOM_COST_CONFIG,
        log_path=LOG_PATH,
    )

    question_total = retrieval_receipt["cost"] + llm_receipt["cost"]
    print(
        f"{question['label']:>2} "
        f"{question['top_k']:>5} "
        f"{retrieved_context_tokens:>9} "
        f"{llm_input_tokens:>10} "
        f"{dollars(estimated_generation_cost):>10} "
        f"{dollars(question_total):>8} "
        f"{dollars(budget.spent):>11}"
    )

summary = budget.summary()
session_cost = summary["spent"]
classroom_projection = session_cost * 40 * 5

print("\nSession summary")
print("---------------")
print(f"Started with: {dollars(summary['budget_total'])}")
print(f"Total session cost: {dollars(session_cost)}")
print(f"Remaining: {dollars(summary['remaining'])}")
print(f"Actions tracked: {summary['number_of_actions']}")
print(f"If 40 students each run this workflow 5 times: {dollars(classroom_projection)}")

ai_receipts = [
    receipt
    for receipt in budget.receipts
    if receipt["category"] in {"rag_embedding", "rag_generation"}
]
non_ai_receipts = [
    receipt
    for receipt in budget.receipts
    if receipt["category"] not in {"rag_embedding", "rag_generation"}
]
ai_usage_cost = sum(receipt["cost"] for receipt in ai_receipts)
non_ai_compute_cost = sum(receipt["cost"] for receipt in non_ai_receipts)
total_tokens = sum(receipt.get("total_tokens", 0) for receipt in ai_receipts)

print("\nAI Usage Summary")
print("----------------")
print(f"- AI usage cost: {dollars(ai_usage_cost)}")
print(f"- Model training cost: {dollars(non_ai_compute_cost)} (non-AI indexing/retrieval)")
print(f"- Number of AI calls: {len(ai_receipts)}")
print(f"- Total tokens used: {total_tokens:,}")
print("\nObservation:")
if ai_usage_cost > non_ai_compute_cost:
    print("You spent more on AI assistance than on the model itself.")
else:
    print("AI assistance was a smaller portion of your total compute cost.")

print("\nWhat to notice")
print("--------------")
print("RAG is not free just because it uses your own documents.")
print("More retrieved context means more input tokens in the generation step.")
print("Chat history and repeated questions quietly increase later prompt sizes.")
print(
    "Chunk size, top-k retrieval, and verbose context all affect cost because "
    "they control how much text gets sent back into the LLM."
)
print(
    "Small per-question costs can become large at classroom or organizational scale."
)
