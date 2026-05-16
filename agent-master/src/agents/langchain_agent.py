# src/agents/langchain_agent.py

from __future__ import annotations

import os
import re
import traceback
from datetime import datetime
from typing import Tuple

from dotenv import load_dotenv

from src.tools.book_loader import extract_pdf_text
from src.tools.narrator import NarratorTool
from src.utils.logger import (
    log_task_start,
    log_task_complete,
    log_info,
    log_section,
)

load_dotenv()


NEW_TASK_KEYWORDS = ["新书", "新文件", "换个", "开始", "另外一本", "另一本"]


def now_timestamp() -> str:
    return datetime.now().isoformat()


class LangChainNarratorAgent:
    """
    稳定版书籍解说 Agent。

    当前版本不依赖 LangChain create_agent。
    流程：
    后端传 PDF 路径 + 页码 + 风格
    ↓
    Agent 自己读取 PDF
    ↓
    Narrator/Gemma 生成解说
    ↓
    返回给后端
    """

    def __init__(self):
        self.context = {
            "tool_calls": []
        }

    def run(self, user_request: str) -> dict:
        try:
            log_section("开始处理请求")
            log_task_start("处理用户请求")

            if any(kw in user_request for kw in NEW_TASK_KEYWORDS):
                log_info("检测到新任务，清空上下文...")
                self.reset_context()

            pdf_path = self._parse_pdf_path(user_request)
            start_page, end_page = self._parse_page_range(user_request)
            style = self._parse_style(user_request)
            reading_mode = self._parse_reading_mode(user_request)
            voice = self._parse_voice(user_request)
            title = self._parse_title(user_request)
            task_instruction = self._parse_task_instruction(user_request)
            print("========== PARSED_TASK_INSTRUCTION ==========")
            print(task_instruction)

            if pdf_path:
                pdf_text = extract_pdf_text(
                    file_path=pdf_path,
                    start_page=start_page,
                    end_page=end_page,
                    max_chars=int(os.getenv("NARRATOR_MAX_INPUT_CHARS", "80000")),
                )

                print("========== PDF_TEXT_LENGTH ==========")
                print(len(pdf_text))

                print("========== PDF_TEXT_PREVIEW ==========")
                print(pdf_text[:1500])

                self.context["last_pdf_path"] = pdf_path
                self.context["last_pdf_text"] = pdf_text
                self.context.setdefault("tool_calls", []).append(
                    {
                        "tool_name": "read_pdf_pages",
                        "input_data": {
                            "file_path": pdf_path,
                            "start_page": start_page,
                            "end_page": end_page,
                        },
                        "output_data": {
                            "text_preview": pdf_text[:300],
                            "length": len(pdf_text),
                        },
                        "timestamp": now_timestamp(),
                    }
                )

                if not pdf_text.strip():
                    return {
                        "success": False,
                        "result": "",
                        "context": self.context,
                        "error": "PDF 指定页码范围内没有提取到文本，可能是扫描版 PDF 或页码范围不包含正文。",
                    }

                content_for_generation = self._compose_generation_content(
                    pdf_text=pdf_text,
                    task_instruction=task_instruction,
                reading_mode=reading_mode,
                )

            else:
                custom_text = self._parse_custom_text(user_request)

                print("========== AGENT_CUSTOM_TEXT_LENGTH ==========")
                print(len(custom_text))

                print("========== AGENT_CUSTOM_TEXT_PREVIEW ==========")
                print(custom_text[:1500])

                if not custom_text.strip():
                    return {
                        "success": False,
                        "result": "",
                        "context": self.context,
                        "error": "未找到 PDF 文件路径，也没有找到可用于生成的自定义文本。",
                    }

                content_for_generation = self._compose_generation_content(
                    pdf_text=custom_text,
                    task_instruction=task_instruction,
                reading_mode=reading_mode,
                )

            narrator = NarratorTool(style=style)

            narration = narrator.generate(
                content=content_for_generation,
                title=title,
                style=style,
                task_instruction=task_instruction,
            )

            if not isinstance(narration, str) or not narration.strip():
                return {
                    "success": False,
                    "result": "",
                    "context": self.context,
                    "error": "Gemma 没有返回有效解说词。",
                }

            narration = narration.strip()

            if narration.startswith("生成失败"):
                return {
                    "success": False,
                    "result": "",
                    "context": self.context,
                    "error": narration,
                }

            self.context["last_narration"] = narration
            self.context.setdefault("tool_calls", []).append(
                {
                    "tool_name": "generate_narration",
                    "input_data": {
                        "title": title,
                        "style": style,
                        "voice": voice,
                        "task_instruction": task_instruction,
                    },
                    "output_data": {
                        "result_preview": narration[:300],
                        "length": len(narration),
                    },
                    "timestamp": now_timestamp(),
                }
            )

            log_task_complete(
                "处理用户请求",
                narration[:200] + "..." if len(narration) > 200 else narration,
            )

            return {
                "success": True,
                "result": narration,
                "context": self.context,
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "success": False,
                "result": "",
                "context": self.context,
                "error": str(e),
            }

    def reset_context(self):
        self.context.clear()
        self.context["tool_calls"] = []
        log_info("上下文已重置")

    def _compose_generation_content(
        self,
        pdf_text: str,
        task_instruction: str,
        reading_mode: str = "quick",
    ) -> str:
        if not task_instruction.strip():
            task_instruction = "请生成一段适合音频播放的中文书籍解说词。"

        return f"""
用户任务要求：
{task_instruction}

阅读模式：
{"深度阅读" if reading_mode == "deep" else "快速阅读"}

PDF 指定页码范围内的原文内容：
{pdf_text}

生成要求：
1. 必须基于以上原文内容完成任务，不要编造原文没有的信息；
2. 如果用户要求分析人物性格，请结合原文中的行为、对话和叙述依据；
3. 如果当前页码范围内依据不足，请明确说明依据不足；
4. 不要暴露本地文件路径；
5. 直接输出最终解说词或分析结果，不要输出工具调用过程。
"""

    def _parse_pdf_path(self, text: str) -> str:
        patterns = [
            r"【PDF 文件路径】\s*(.+)",
            r"PDF 文件路径[:：]\s*(.+)",
            r"文件路径[:：]\s*(.+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                line = match.group(1).strip()
                return line.splitlines()[0].strip()

        return ""

    def _parse_page_range(self, text: str) -> Tuple[int, int]:
        patterns = [
            r"【页码范围】\s*第\s*(\d+)\s*页到第\s*(\d+)\s*页",
            r"第\s*(\d+)\s*页到第\s*(\d+)\s*页",
            r"第\s*(\d+)\s*页\s*-\s*第\s*(\d+)\s*页",
            r"start_page[:：]\s*(\d+).*?end_page[:：]\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.S)
            if match:
                return int(match.group(1)), int(match.group(2))

        return 1, 3

    def _parse_style(self, text: str) -> str:
        match = re.search(r"【解说风格】\s*(.+)", text)
        if match:
            return match.group(1).strip().splitlines()[0]

        for style in ["短视频", "睡前故事", "电影解说"]:
            if style in text:
                return style

        return "短视频"

    def _parse_voice(self, text: str) -> str:
        match = re.search(r"【声音偏好】\s*(.+)", text)
        if match:
            return match.group(1).strip().splitlines()[0]

        for voice in ["晓晓", "云希", "云扬", "晓伊"]:
            if voice in text:
                return voice

        return "晓晓"

    def _parse_title(self, text: str) -> str:
        match = re.search(r"【书名】\s*《?([^》\n]+)》?", text)
        if match:
            return match.group(1).strip()

        match = re.search(r"书名[:：]\s*《?([^》\n]+)》?", text)
        if match:
            return match.group(1).strip()

        match = re.search(r"【资料来源】\s*(.+)", text)
        if match:
            return match.group(1).strip().splitlines()[0]

        return "书籍解说"

    def _parse_reading_mode(self, text: str) -> str:
        if "深度阅读" in text or "深度解说" in text or "deep" in text:
            return "deep"
        return "quick"

    def _parse_task_instruction(self, text: str) -> str:
        """
        解析用户额外要求。
        优先提取后端传来的【用户额外要求】字段。
        """
        import re

        if not text:
            return ""

        patterns = [
            r"【用户额外要求】\s*(.*?)(?=\n\n【|\n【阅读模式要求】|\n【内容规则】|\n【写作要求】|\n【输出规则】|\Z)",
            r"用户额外要求[:：]\s*(.*?)(?=\n\n【|\n【阅读模式要求】|\n【内容规则】|\n【写作要求】|\n【输出规则】|\Z)",
            r"用户任务要求[:：]\s*(.*?)(?=\nPDF|\n阅读模式|\n生成要求|\Z)",
            r"额外要求[:：]\s*(.*?)(?=\nPDF|\n生成要求|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.S)
            if match:
                value = match.group(1).strip()
                if value:
                    default_phrases = [
                        "请根据原文情节重新讲述故事",
                        "不要写主题总结",
                        "不要编造原文没有的内容",
                        "请生成一段适合音频播放的中文书籍解说词",
                    ]

                    # 如果只是系统默认话术，就不当作用户额外任务
                    if any(phrase in value for phrase in default_phrases) and len(value) < 80:
                        return ""

                    return value

        return ""


    def _parse_custom_text(self, text: str) -> str:
        patterns = [
            r"【文本内容】\s*(.*?)(?:\n【|\Z)",
            r"书籍原文片段如下[:：]\s*(.*?)(?:\Z)",
            r"PDF 原文内容[:：]\s*(.*?)(?:\n生成要求[:：]|\Z)",
            r"PDF 指定页码范围内的原文内容[:：]\s*(.*?)(?:\n生成要求[:：]|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.S)
            if match:
                return match.group(1).strip()

        return ""