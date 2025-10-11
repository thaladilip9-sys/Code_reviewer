# toolkits.py
from langchain.agents import Tool
from src.tools.code_standard_tool import CodeStandardsChecker

# Convert checkers to LangChain tools
standards_tool = CodeStandardsChecker().get_tool()

# Async runner for LangChain tools
async def run_tool(tool, input_data):
    """Run a tool with proper async handling"""
    try:
        if hasattr(tool.func, '__call__'):
            # Handle async functions
            if hasattr(tool.func, '__await__'):
                result = await tool.func(input_data)
            else:
                # For sync functions, run in thread pool
                import asyncio
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, tool.func, input_data)
            return result
        return str(tool)
    except Exception as e:
        return f"Tool execution error: {str(e)}"