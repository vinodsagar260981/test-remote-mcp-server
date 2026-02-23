# mcp_client.py

import asyncio
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage
from dotenv import load_dotenv
import os

load_dotenv()

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "C:\\Users\\vinod\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\uv.exe",
        "args": [
            "run",
            "fastmcp",
            "run",
            "C:\\Users\\vinod\\OneDrive\\Desktop\\Coding\\AIWorld\\MCP_Tutorial\\math.py"
        ]
    },
    "sqlAgent": {
        "transport": "stdio",
        "command": "C:\\Users\\vinod\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\uv.exe",
        "args": [
            "run",
            "fastmcp",
            "run",
            "C:\\Users\\vinod\\OneDrive\\Desktop\\Coding\\AIWorld\\MCP_Tutorial\\sqlproject.py"
        ]
    },
    "expense": {
        "transport": "streamable_http",
        "url": "https://reliable-brown-ostrich.fastmcp.app/mcp",
        "headers": {
            "Authorization": f"Bearer {os.getenv('FASTMCP_API_KEY')}"
        }
    }
}




async def run_agent(prompt: str):
    client = MultiServerMCPClient(SERVERS)  # type: ignore
    tools = await client.get_tools()

    named_tools = {tool.name: tool for tool in tools}
    
    print("Available Tools: ", named_tools.keys())

    llm = ChatGroq(model="openai/gpt-oss-safeguard-20b")
    llm_with_tools = llm.bind_tools(tools)

    response = await llm_with_tools.ainvoke(prompt)

    # If no tool call → return direct answer
    if not getattr(response, "tool_calls", None):
        return response.content

    tool_messages = []

    for tc in response.tool_calls:
        tool_name = tc["name"]
        tool_args = tc.get("args") or {}
        tool_id = tc["id"]

        result = await named_tools[tool_name].ainvoke(tool_args)

        tool_messages.append(
            ToolMessage(
                tool_call_id=tool_id,
                content=json.dumps(result)
            )
        )

    final_result = await llm_with_tools.ainvoke(
        [prompt, response, *tool_messages]
    )

    return final_result.content