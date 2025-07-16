from fastapi import FastAPI
from langchain.prompts.chat import ChatPromptTemplate
#from langchain.chat models import ChatOpenAI
from langserve import add_routes
import uvicorn
import os
from langchain_community.llms import ollama
from dotenv import load_dotenv


load_dotenv()

os.environ["LANGSERVE_API_KEY"] = os.getenv("LANGSERVE_API_KEY")  # we have to give api key here 


app = FastAPI(
    title="Langchain server",
    version="0.1.0",
    description="A normal langchain server",
    
)

model = ChatOpenAI

add_routes(
    app(),
    model(),
    path="/ollama2"
)

llm = Ollama(model="llama2")

prompt = ChatPromptTemplate.from_template("You are a helpful assistant. {input}")

llm(prompt.format(input="What is Langchain?"))

add_routes(
    app,
    prompt|llm,
    path="/ollama2"
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

