import json
import pandas as pd

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# -----------------------
# Load results
# -----------------------

df = pd.read_csv("1mil20260716_112330_rag_evaluation_results.csv")

# -----------------------
# Judge model
# -----------------------

judge = ChatOllama(
    model="llama3.2:1b",
    temperature=0
)

template = """
# Context

You are an impartial evaluator for a Retrieval-Augmented Generation (RAG) question-answering system.

Your role is to fairly judge whether the generated answer conveys the same meaning as the expected answer.

You are evaluating semantic correctness, NOT writing style.

Assume:
- The expected answer is the reference answer.
- Different wording, sentence structure, or ordering should NOT reduce the score if the meaning is preserved.
- Be neither overly strict nor overly generous.
- Ignore grammar, spelling, verbosity, and formatting unless they change the meaning.
- Penalize factual errors, contradictions, unsupported claims, or hallucinated information.
- If the generated answer contains both correct and incorrect information, lower the score accordingly.

# Goal

Compare the generated answer against the expected answer and assign a score from 0 to 5.

Scoring rubric:

5 = Semantically equivalent. Includes all important information. May use different wording.

4 = Mostly correct. Missing only minor details or contains insignificant inaccuracies.

3 = Partially correct. Captures some key information but misses important points or includes noticeable inaccuracies.

2 = Mostly incorrect. Only a small portion is correct or contains major factual errors.

1 = Incorrect. Almost none of the expected information is present.

0 = Completely incorrect, irrelevant, or primarily hallucinated.

# Evaluation Data

Question:
{question}

Expected Answer:
{expected}

Generated Answer:
{answer}

# Output Format

Return ONLY valid JSON.

Example:

{{
    "score": 4,
    "passed": true,
    "reason": "Mentions gluten-free crust but omits cauliflower."
}}
"""

prompt = ChatPromptTemplate.from_template(template)

chain = prompt | judge

# -----------------------
# Evaluate
# -----------------------

scores = []

for _, row in df.iterrows():

    response = chain.invoke({
        "question": row["Query"],
        "expected": row["Expected"],
        "answer": row["Answer"]
    })

    text = response.content.strip()

    try:
        result = json.loads(text)
    except Exception:
        print(text)
        result = {
            "score": None,
            "passed": False,
            "reason": "Judge did not return valid JSON."
        }

    scores.append(result)

# -----------------------
# Save results
# -----------------------

df["Judge Score"] = [x["score"] for x in scores]
df["Judge Passed"] = [x["passed"] for x in scores]
df["Judge Reason"] = [x["reason"] for x in scores]

print(df[[
    "ID",
    "Judge Score",
    "Judge Passed"
]])

print("\nAverage Judge Score:",
      df["Judge Score"].dropna().mean())

df.to_csv("llm_judge_results.csv", index=False)