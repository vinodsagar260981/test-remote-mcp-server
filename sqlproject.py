from fastmcp import FastMCP
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

load_dotenv()

mcp = FastMCP("SQLBot")


llm = ChatGroq(model="openai/gpt-oss-safeguard-20b")

@mcp.tool
def write_sql(question: str)->str:
    """
    Generate SQL query for PostgreSQL/MySQL based on user question.
    """
    messages = [
        SystemMessage(content="You are an expert SQL query generator for PostgreSQL and MySQL."),
        HumanMessage(content=question)
    ]

    response = llm.invoke(messages)

    return response.content # type: ignore

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)