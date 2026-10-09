from pathlib import Path
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

env_file = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_file)

print("GROQ_API_KEY set:", bool(os.getenv("GROQ_API_KEY")))

from trip_planner.agents.trip_flow import GraphBuilder

app = FastAPI()
builder = GraphBuilder()
graph = builder.build_graph()

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/query")
async def query(req: QueryRequest):
    state = {"messages": [HumanMessage(content=req.query)]}
    result = graph.invoke(state)
    print("Result:---", result)
    return {"response": result["messages"][-1].content}