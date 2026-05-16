# main.py

import sys
from pathlib import Path
import time

# 添加项目路径 
sys.path.append(str(Path(__file__).parent))
from src.agents.langchain_agent import LangChainNarratorAgent

def main():
    print("=" * 60)
    print("🤖 多轮对话音视频解说 Agent（输入'退出'结束）")
    print("=" * 60)
    
    # 创建 Agent（记忆会保留在整个会话中）
    agent = LangChainNarratorAgent()
    
    while True:
        # 获取用户输入
        if len(sys.argv) > 1:
            user_request = " ".join(sys.argv[1:])
            # 清空参数，避免每次都走这个分支
            sys.argv = [sys.argv[0]]
        else:
            print("\n请输入你的请求:")
            user_request = input(">>> ").strip()
        
        if user_request.lower() in ["退出", "exit", "quit", "q"]:
            print("👋 再见！")
            break
        
        if not user_request:
            continue
        
        print("\n🤖 Agent: ", end="", flush=True)
        
        # 运行 Agent
        result = agent.run(user_request)
        if not result.get("success"):
            print(f"\n\n❌ 错误: {result.get('error')}")
        else:
            print(result.get("result", ""))
        
        print()  # 换行

if __name__ == "__main__":
    import logging
    # 关闭 httpx 的日志
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    main()
