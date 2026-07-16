from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from mqtt_client import retrieve_context
from config import OLLAMA_MODEL



model = OllamaLLM(
    model=OLLAMA_MODEL
)



template = """
# Context
You are a question-answering assistant for a restaurant. Your only source of truth is the collection of customer reviews provided below.

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


prompt = ChatPromptTemplate.from_template(
    template
)


chain = (
    prompt
    |
    model
)



def ask_agent(
    question: str
):

    #
    # Agent decides retrieval is needed
    #

    context = retrieve_context(
        question
    )


    matches = context.get(
        "matches",
        []
    )


    if not matches:

        return (
            "I don't know based on "
            "the provided reviews."
        )


    reviews = "\n\n".join(
        [
            item["content"]
            for item in matches
        ]
    )


    result = chain.invoke(
        {
            "reviews": reviews,
            "question": question
        }
    )


    return result
