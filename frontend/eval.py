from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from mqtt_client import retrieve_context
from config import OLLAMA_MODEL

import json
import pandas as pd
from datetime import datetime
import time

# -----------------------------
# Load test set
# -----------------------------
with open("test-cases.json", "r", encoding="utf-8") as f:
    test_set = json.load(f)

# -----------------------------
# LLM
# -----------------------------
model = OllamaLLM(
    model=OLLAMA_MODEL
)

template = """
# Context
You are a question-answering assistant for a pizza restaurant. Your only source of truth is the collection of customer reviews provided below.

The reviews may contain opinions, personal experiences, conflicting statements, or incomplete information. Treat them as evidence rather than objective facts.

# Goal
Answer the user's question using ONLY information that can be supported by the provided reviews.

Rules:
- Never use outside knowledge.
- Do not assume or infer facts that are not mentioned.
- If multiple reviews agree, summarize the consensus.
- If reviews disagree, explain the different viewpoints.
- If the reviews do not provide enough information to answer confidently, respond with:
  "I don't know based on the provided reviews."
- Do not mention information that is not present in the reviews.

# Reviews
{reviews}

# User Question
{question}

# Output Format
Provide your answer in the following format:

Answer:
<concise answer supported by the reviews>

Evidence:
- <key review finding 1>
- <key review finding 2>
- <key review finding 3 (if applicable)>
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# -----------------------------
# Evaluation
# -----------------------------
results = []

for test in test_set:

    print(f"Evaluating {test['id']}...")

    start_time = time.time()

    # -----------------------------
    # Retrieve reviews via MQTT
    # -----------------------------
    context = retrieve_context(test["query"])

    matches = context.get("matches", [])

    expected = test["expected"]
    if isinstance(expected, list):
        expected = ", ".join(expected)

    if not matches:
        results.append({
            "ID": test["id"],
            "Query": test["query"],
            "Expected": expected,
            "Answer": "No relevant reviews found.",
            "Response time": time.time() - start_time
        })
        continue

    # -----------------------------
    # Build review text
    # -----------------------------
    reviews_text = "\n\n".join(
        item["content"]
        for item in matches
    )

    # -----------------------------
    # Generate answer
    # -----------------------------
    answer = chain.invoke({
        "reviews": reviews_text,
        "question": test["query"]
    })

    response_time = time.time() - start_time

    results.append({
        "ID": test["id"],
        "Query": test["query"],
        "Expected": expected,
        "Answer": answer,
        "Response time": response_time
    })

# -----------------------------
# Save Results
# -----------------------------
df = pd.DataFrame(results)

filename = f"{datetime.now():%Y%m%d_%H%M%S}_rag_evaluation_results.csv"
df.to_csv(filename, index=False)

print(f"\nDetailed results written to {filename}")