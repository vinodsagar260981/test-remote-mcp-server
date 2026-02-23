import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
import json

load_dotenv()

SERVERS = {
    "math":{
        "transport": "stdio",
        "command": "C:\\Users\\vinod\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\uv.exe",
        "args": [
        "run",
        "fastmcp",
        "run",
        "C:\\Users\\vinod\\OneDrive\\Desktop\\Coding\\AIWorld\\MCP_Tutorial\\Sqlmcp\\math.py"
      ]
    }
}

async def main():
    client = MultiServerMCPClient(SERVERS) # type: ignore
    tools = await client.get_tools()
    # 
    named_tools = {}
    for tool in tools:
        named_tools[tool.name] = tool
    
    # print(named_tools)
    
    llm = ChatGroq(model="openai/gpt-oss-safeguard-20b")
    llm_with_tools = llm.bind_tools(tools)
    
    
    prompt = input("Type here: ")
    response = await llm_with_tools.ainvoke(prompt)
    
    if not getattr(response, "tool_calls", None):
        print("\n LLM Reply:", response.content)
        return 
    
    # selected_tools =  response.tool_calls[0]["name"]
    # selected_tools_args = response.tool_calls[0]["args"]
    # selected_tool_id = response.tool_calls[0]["id"]
    
    tool_messages = []
    for tc in response.tool_calls:
        selected_tools = tc["name"]
        selected_tools_args = tc.get("args") or {}
        selected_tool_id = tc["id"]
    
        result = await named_tools[selected_tools].ainvoke(selected_tools_args)
        tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))


    
    final_result = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print(f"Final Result - {final_result.content}")
    
    
if __name__=="__main__":
    asyncio.run(main())
    