"""
test: 给 tests/test_3p_1k.txt 的每一章写一个简短叙述并保存

运行方式:
    python tests/test_00/test.py
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from src.tools.langchain_tools import get_all_tools
from src.prompts.agent_prompts import SystemPromptBuilder
from src.utils.logger import (
    log_task_start, log_task_step, log_task_complete,
    log_info, log_section
)


load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"),
    api_key=os.getenv("API_KEY_ENV"),
    base_url=os.getenv("BASE_URL")
)

context = {}

tools = get_all_tools(context)

system_prompt = SystemPromptBuilder(tools).build()

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

query = "给 tests/test_3p_1k.txt 的第一章写一个简短叙述并保存"

if __name__ == "__main__":
    import logging
    # 关闭 httpx 的日志
    logging.getLogger("httpx").setLevel(logging.WARNING)

    try:
        log_section("开始处理请求")
        log_task_start("处理用户请求")
        
        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]}
        )
        
        final_answer = result.get("messages", [])[-1].content if isinstance(result, dict) else str(result)
            
        log_task_complete("处理用户请求", final_answer[:200] + "..." if len(final_answer) > 200 else final_answer)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(str(e))
