from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import SessionLocal
from models import UserQuery
from ollama_client import get_ollama_response

from pydantic import BaseModel

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QueryRequest(BaseModel):
    user_query: str

@app.post("/query")
def submit_query(request: QueryRequest, db: Session = Depends(get_db)):
    # Save query to DB
    new_query = UserQuery(query=request.user_query)
    db.add(new_query)
    db.commit()
    db.refresh(new_query)

    # Call Ollama with context
    history = [{"role": "user", "content": request.user_query}]
    reply = get_ollama_response(history)

    # Save response
    new_query.response = reply
    db.commit()

    return {"query_id": new_query.id, "response": reply}

@app.get("/response/{query_id}")
def get_query_response(query_id: int, db: Session = Depends(get_db)):
    query = db.query(UserQuery).filter(UserQuery.id == query_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return {"query": query.query, "response": query.response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)