# test_all_servers.py
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": "C:\\Users\\vinod\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\uv.exe",
        "args": ["run", "fastmcp", "run", "C:\\Users\\vinod\\OneDrive\\Desktop\\Coding\\AIWorld\\MCP_Tutorial\\math.py"]
    },
    "sqlAgent": {
        "transport": "stdio",
        "command": "C:\\Users\\vinod\\AppData\\Local\\Programs\\Python\\Python312\\Scripts\\uv.exe",
        "args": ["run", "fastmcp", "run", "C:\\Users\\vinod\\OneDrive\\Desktop\\Coding\\AIWorld\\MCP_Tutorial\\sqlproject.py"]
    },
    "expense": {
        "transport": "streamable_http",
        "url": "http://localhost:8000/mcp"
    }
}

# Test each server individually
async def test_single(name, config):
    try:
        client = MultiServerMCPClient({name: config})
        tools = await client.get_tools()
        print(f"✅ {name}: {[t.name for t in tools]}")
    except Exception as e:
        print(f"❌ {name}: {e}")

async def test():
    for name, config in SERVERS.items():
        await test_single(name, config)

asyncio.run(test())