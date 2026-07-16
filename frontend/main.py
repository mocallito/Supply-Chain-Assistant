from fastapi import FastAPI
from pydantic import BaseModel

from agent import ask_agent


app = FastAPI(
    title="Restaurant Review Agent API"
)


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    answer: str



@app.post(
    "/chat",
    response_model=ChatResponse
)
async def chat(
    request: ChatRequest
):

    result = ask_agent(
        request.prompt
    )

    return {
        "answer": result
    }
