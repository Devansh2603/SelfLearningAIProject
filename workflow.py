from langchain.chat_models import ChatOllama
from sqlalchemy import text
from langgraph.graph import StateGraph, END

# --- Configuration ---
VALID_TABLES = ['customer_vehicle_info', 'job_card_details', 'vehicle_service_details', 'vehicle_service_summary']

# Ollama models
llm_sql = ChatOllama(model="llama3")
llm_nl = ChatOllama(model="mistral")

# --- Helper Prompts ---
def sql_prompt(user_query: str) -> str:
    return f"""
You are an expert SQL assistant. Convert the following natural language request to a valid SQL query using only these tables: 
{', '.join(VALID_TABLES)}.
Respond with only the SQL query.

User Request: "{user_query}"
"""

def humanize_prompt(original_query, sql_result):
    return f"""
You are a helpful assistant. The following is a result of an SQL query:

Original Query: "{original_query}"
SQL Output: {sql_result}

Please summarize this result clearly in simple English.
"""

# --- Workflow Nodes ---
def validate(state):
    query = state["user_input"].lower()
    if not any(table in query for table in VALID_TABLES):
        return {"response": "❌ Query not related to allowed tables."}
    return state

def clean_query(state):
    state["clean_query"] = state["user_input"].strip().replace("?", "")
    return state

def generate_sql(state):
    prompt = sql_prompt(state["clean_query"])
    sql = llm_sql.predict(prompt).strip()
    state["sql_query"] = sql
    return state

# ✅ This function will require session injection at runtime
def execute_sql(state, session):
    try:
        result = session.execute(text(state["sql_query"]))
        rows = result.fetchall()
        state["sql_result"] = [dict(row._mapping) for row in rows]
    except Exception as e:
        state["sql_result"] = f"❌ Error: {str(e)}"
    return state

def humanize_response(state):
    if isinstance(state["sql_result"], str) and state["sql_result"].startswith("❌"):
        state["response"] = state["sql_result"]
    else:
        prompt = humanize_prompt(state["user_input"], state["sql_result"])
        response = llm_nl.predict(prompt)
        state["response"] = response.strip()
    return state

# --- LangGraph Setup Function (requires injected `session` at runtime) ---
def get_langgraph_workflow(session):
    def exec_node(state):
        return execute_sql(state, session)

    workflow = StateGraph()
    workflow.add_node("validate", validate)
    workflow.add_node("clean_query", clean_query)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", exec_node)
    workflow.add_node("humanize", humanize_response)

    workflow.set_entry_point("validate")
    workflow.add_edge("validate", "clean_query")
    workflow.add_edge("clean_query", "generate_sql")
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_edge("execute_sql", "humanize")
    workflow.add_edge("humanize", END)

    return workflow.compile()
