from fastapi import FastAPI
from pydantic import BaseModel
from workflow import get_langgraph_workflow

app = FastAPI()
workflow = get_langgraph_workflow()

class QueryRequest(BaseModel):
    user_query: str

@app.post("/query")
def ask_query(requests: QueryRequest):
    result = workflow.invoke({"user_input": requests.user_query})
    return {"response": result.get("response", "No response")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)