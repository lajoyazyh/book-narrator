# src/tools/narrator.py
from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class NarratorTool:
    """
    书籍解说生成工具。

    quick：快速阅读，400-800字，适合快速了解。
    deep：深度阅读，2000-3500字，保留更多人物、事件、对话、心理、因果和细节。
    """

    MAX_INPUT_CHARS = int(os.getenv("NARRATOR_MAX_INPUT_CHARS", "80000"))

    def __init__(self, api_key: Optional[str] = None, style: str = "短视频"):
        self.client = OpenAI(
            api_key=api_key or os.getenv("API_KEY_ENV", "ollama"),
            base_url=os.getenv("BASE_URL", "http://localhost:11434/v1"),
        )
        self.default_style = style
        self.model = os.getenv("MODEL_NAME", "gemma4:26b")

    def generate(
        self,
        content: str,
        title: str = "",
        chapter_number: Optional[int] = None,
        style: Optional[str] = None,
        task_instruction: str = "",
        reading_mode: str = "quick",
        **kwargs,
    ) -> str:
        current_style = style or self.default_style
        source_text = self._extract_source_text(content)

        if not source_text.strip():
            source_text = content.strip()

        reading_mode = self._detect_reading_mode(
            reading_mode=reading_mode,
            content=content,
            task_instruction=task_instruction,
        )

        source_text = source_text[: self.MAX_INPUT_CHARS]

        # 根据输入文本长度动态设置输出长度
        # quick：压缩为较短解说
        # deep：尽量输出为输入文本的约 1/3，但设置上下限，避免过短或过长
        if reading_mode == "deep":
            target_chars = max(2500, min(9000, len(source_text) // 3))
            min_chars = max(1800, int(target_chars * 0.75))
            max_chars = int(target_chars * 1.2)
        else:
            min_chars = 400
            max_chars = 900

        if reading_mode == "deep":
            prompt = self._build_deep_prompt(
                source_text=source_text,
                title=title,
                style=current_style,
                task_instruction=task_instruction,
                min_chars=min_chars,
                max_chars=max_chars,
            )
            max_tokens = 9000
            temperature = 0.18
        else:
            prompt = self._build_quick_prompt(
                source_text=source_text,
                title=title,
                style=current_style,
                task_instruction=task_instruction,
            )
            max_tokens = 1200
            temperature = 0.22

        self._save_debug_prompt(prompt, current_style, reading_mode)

        print("========== READING_MODE ==========")
        print(reading_mode)
        print("========== SOURCE_TEXT_LENGTH ==========")
        print(len(source_text))
        print("========== TARGET_OUTPUT_CHARS ==========")
        print(min_chars, max_chars)
        print("========== USER_PROMPT_LENGTH ==========")
        print(len(prompt))
        print("========== USER_PROMPT_PREVIEW ==========")
        print(prompt[:3000])

        raw = self._call_model(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        print("========== RAW_NARRATION ==========")
        print(raw)
        print("========== RAW_NARRATION_LENGTH ==========")
        print(len(raw or ""))

        result = self._clean_output(raw or "")

        print("========== CLEANED_NARRATION ==========")
        print(result)
        print("========== CLEANED_NARRATION_LENGTH ==========")
        print(len(result))

        # 第二阶段：如果用户填写了额外任务，则单独调用模型完成额外任务
        if self._need_extra_task(task_instruction):
            print("========== EXTRA_TASK_TRIGGERED ==========")
            print(task_instruction)

            extra_prompt = self._build_extra_task_prompt(
                source_text=source_text,
                narration_text=result,
                task_instruction=task_instruction,
                title=title,
            )

            print("========== EXTRA_TASK_PROMPT_PREVIEW ==========")
            print(extra_prompt[:3000])

            extra_raw = self._call_model(
                prompt=extra_prompt,
                temperature=0.18,
                max_tokens=5000,
            )

            print("========== EXTRA_TASK_RAW ==========")
            print(extra_raw)
            print("========== EXTRA_TASK_RAW_LENGTH ==========")
            print(len(extra_raw or ""))

            extra_result = self._clean_output(extra_raw or "")

            print("========== EXTRA_TASK_CLEANED ==========")
            print(extra_result)
            print("========== EXTRA_TASK_CLEANED_LENGTH ==========")
            print(len(extra_result))

            if extra_result.strip():
                result = result.rstrip() + "\n\n" + extra_result.strip()

        return result

    def _detect_reading_mode(
        self,
        reading_mode: Optional[str],
        content: str,
        task_instruction: str,
    ) -> str:
        text = f"{reading_mode or ''}\n{content or ''}\n{task_instruction or ''}"

        if any(key in text for key in ["deep", "深度阅读", "深度解说", "详细阅读", "详细解说"]):
            return "deep"

        return "quick"

    def _build_quick_prompt(
        self,
        source_text: str,
        title: str,
        style: str,
        task_instruction: str = "",
    ) -> str:
        style_rule = self._style_rule(style)
        extra_rule = self._extra_instruction_rule(task_instruction)

        return f"""
请根据下面 PDF 原文，生成一段解说。

书名或章节：{title}

阅读模式：快速阅读

快速阅读要求：
1. 直接从原文人物或事件切入；
2. 只讲原文中发生的事情，不扩展原文之外内容；
3. 使用原文中出现的人名和事件；
4. 语言适合口播，有节奏；
5. 压缩次要描写，保留主要人物、关键事件和重要转折；
6. 输出 400-800 字正文。

{style_rule}

{extra_rule}

额外要求执行规则：
- 如果用户额外要求为空，则只生成解说正文；
- 如果用户额外要求中包含“分析”“人物性格”“文章风格”“主题”“评价”等要求，必须在解说正文后继续补充对应分析；
- 分析内容必须基于原文，不要脱离文本发挥；
- 如果用户要求“最后加入”，就必须放在解说正文之后；
- 不要因为前面已经完成故事解说就忽略用户额外要求。

PDF 原文：
{source_text}

现在直接输出正文；如果用户额外要求包含分析任务，请在正文后继续输出对应分析。
"""

    def _build_deep_prompt(
        self,
        source_text: str,
        title: str,
        style: str,
        task_instruction: str = "",
        min_chars: int = 2000,
        max_chars: int = 3500,
    ) -> str:
        style_rule = self._style_rule(style)
        extra_rule = self._extra_instruction_rule(task_instruction)

        return f"""
请根据下面 PDF 原文，生成一篇深度阅读版解说。

书名或章节：{title}

阅读模式：深度阅读

核心任务：
你不是写摘要，也不是写读后感，而是要把这一段原文中的情节，按照发生顺序重新讲给听众。因为原文页数较多，所以不能只写几百字概括，必须保留足够细节。

深度阅读要求：
1. 按原文情节顺序展开，不要跳跃式总结；
2. 需要分阶段讲清楚人物经历，例如家庭破败、谋生、家珍回家、被抓壮丁、战场经历、返乡后的变化等；
3. 每个重要事件都要说明：谁做了什么，为什么发生，过程如何，结果怎样；
4. 保留原文中的关键人物、具体动作、重要对话、人物心理、冲突变化和事件后果；
5. 不要添加原文没有的人物、原因、地点、心理或结局；
6. 不要写“故事讲述了”“本文反映了”“主题是”等总结式表达；
7. 不要把几十页内容压缩成一小段，不要只列主要事件；如果原文很长，必须按阶段展开，每个阶段至少讲清楚主要人物、事件经过、冲突、结果和人物反应；
8. 输出不少于 {min_chars} 字，尽量控制在 {min_chars} 到 {max_chars} 字之间；


【多问题去重与合并规则】
在回答用户提出的多个分析要求前，必须先判断这些要求是否语义重复或高度相近。

如果多个要求属于同一分析类型，只能合并为一个栏目回答，不要重复生成多个相似栏目。

合并规则如下：
1. “文章风格分析”“解说风格”“整体风格”“语言风格”“叙事风格”“写作风格”都归为同一类，统一输出为“文章风格分析”。
2. “人物分析”“人物性格分析”“解析出现的人物”“角色分析”都归为同一类，统一输出为“人物分析”或“解析出现的人物”，不要重复列两个栏目。
3. “情节分析”“故事情节”“主要情节”“剧情梳理”“情节发展”都归为同一类，统一输出为“情节分析”。
4. “主题分析”“主旨分析”“中心思想”“思想内涵”“文章主题”都归为同一类，统一输出为“主题分析”。
5. “语言特色”“语言特点”“表达特色”“修辞特点”都归为同一类，统一输出为“语言特色分析”。
6. “内容总结”“故事概括”“主要内容”“情节概括”都归为同一类，统一输出为“内容概括”。

如果用户同时提出多个不同类型的问题，例如“人物分析、情节分析、主题分析”，可以分别回答。
如果用户提出多个相同类型的问题，例如“文章风格分析、解说整个文章的风格”，只能回答一次。

每个栏目只出现一次。
不要换一个标题重复讲同一件事。
不要为了显得完整而重复扩写已经回答过的内容。

【人物解析层级规则】
如果用户要求“快速阅读”“快速解读”“简要解析”“快速分析”，人物解析只保留对当前情节和主题有核心作用的主要人物，通常控制在 3—5 人。不要机械罗列所有出现过的人名或身份称呼。次要人物、工具性人物、只出现一次且没有明显性格展开的人物，不要单独列入人物解析。

如果用户要求“深度阅读”“深度解读”“深入分析”“详细分析”，人物解析需要区分“主要人物”和“次要人物”。主要人物要结合情节进行较完整的性格、行为和作用分析；次要人物只需简要说明身份和情节作用。深度阅读的人物覆盖范围应不少于快速阅读。

如果用户没有明确指定快速或深度模式，默认按“主要人物优先”的方式输出，避免堆砌边缘人物。

9. 可以自然分段。故事解说部分不要使用栏目标题；如果用户要求分析，可以使用“文章风格分析”“人物性格分析”等简短小标题。不要使用编号、Markdown、镜头提示或背景音乐。

{style_rule}

{extra_rule}

额外要求执行规则：
- 如果用户额外要求为空，则只生成解说正文；
- 如果用户额外要求中包含“分析”“人物性格”“文章风格”“主题”“评价”等要求，必须在解说正文后继续补充对应分析；
- 分析内容必须基于原文，不要脱离文本发挥；
- 如果用户要求“最后加入”，就必须放在解说正文之后；
- 不要因为前面已经完成故事解说就忽略用户额外要求。

PDF 原文：
{source_text}

现在直接输出深度阅读正文；如果用户额外要求包含分析任务，请在正文后继续输出对应分析。
"""

    def _extra_instruction_rule(self, task_instruction: str) -> str:
        if not task_instruction or not task_instruction.strip():
            return "用户没有提出额外分析要求，只需要完成解说正文。"

        instruction = task_instruction.strip()

        analysis_keywords = [
            "分析", "人物性格", "性格分析", "文章风格", "写作风格",
            "语言风格", "叙事风格", "主题分析", "最后加入"
        ]

        if any(keyword in instruction for keyword in analysis_keywords):
            return f"""
用户额外要求必须执行：
{instruction}

请严格按下面结构输出：
第一部分：故事解说正文
第二部分：文章风格分析
第三部分：人物性格分析

要求：
- 第一部分按原文情节讲述；
- 第二部分分析文章语言、叙事方式、氛围和表达特点；
- 第三部分分析原文中出现的主要人物性格，例如福贵、家珍、凤霞、有庆、龙二、春生、老全等；只分析原文涉及到的人物；
- 分析必须基于原文事件和细节，不要空泛套话。
"""

        return f"""
用户额外要求必须执行：
{instruction}
请在解说正文中或正文之后回应这个要求，不要忽略。
"""

    def _style_rule(self, style: str) -> str:
        if style == "短视频":
            return """
短视频口播风格要求：
- 可以有“注意看”式的口播感，但不要强行编“小帅”“小美”；
- 优先使用原文真实人物名，例如福贵、家珍、凤霞、有庆、龙二、春生、老全；
- 语言要有节奏，但不能变成空泛鸡汤；
- 不要写背景音乐、镜头、栏目标题。
"""
        if style == "电影解说":
            return """
电影解说风格要求：
- 语言有画面感和叙事感；
- 突出人物处境、冲突和转折；
- 不要写镜头提示、背景音乐或音效。
"""
        if style == "睡前故事":
            return """
睡前故事风格要求：
- 语言温和、自然、舒缓；
- 保持故事顺序清楚；
- 不要改写成童话，不要加入原文没有的情节。
"""
        return "语言自然连贯，按情节顺序讲述。"

    def _need_extra_task(self, task_instruction: str) -> bool:
        """
        判断用户是否真的提出了额外任务。

        人物相关任务不再触发第二阶段 extra_task，
        避免第一阶段已经输出“解析出现的人物”后，
        第二阶段又额外生成“人物性格分析”，造成重复。
        """
        instruction = (task_instruction or "").strip()

        if not instruction:
            return False

        # 人物类任务直接交给第一阶段处理，不进入第二阶段
        person_keywords = [
            "解析出现的人物",
            "出现的人物",
            "人物",
            "人物分析",
            "人物性格",
            "人物性格分析",
            "角色",
            "角色分析",
        ]

        if any(keyword in instruction for keyword in person_keywords):
            return False

        # 过滤后端默认的泛化要求，避免没有真实额外要求时也触发第二任务
        default_like_phrases = [
            "请根据原文情节重新讲述故事",
            "不要写主题总结",
            "不要编造原文没有的内容",
        ]

        if len(instruction) < 80 and any(phrase in instruction for phrase in default_like_phrases):
            return False

        # 只有明确的非人物类分析任务才进入第二阶段
        extra_keywords = [
            "文章风格",
            "写作风格",
            "语言风格",
            "主题分析",
            "情节分析",
            "结构分析",
            "象征意义",
            "主旨",
            "中心思想",
            "写作手法",
        ]

        return any(keyword in instruction for keyword in extra_keywords)

    def _build_extra_task_prompt(
        self,
        source_text: str,
        narration_text: str,
        task_instruction: str,
        title: str = "",
    ) -> str:
        """
        第二阶段 prompt：
        只执行用户额外任务，不重复第一阶段解说正文。
        """
        return f"""
你现在执行第二个独立任务。第一阶段的故事解说已经完成，现在不要重复解说正文，只完成用户提出的额外任务。

书名或章节：
{title}

用户额外任务：
{task_instruction}

第一阶段已经生成的解说正文：
{narration_text}

PDF 原文：
{source_text}

第二任务执行规则：
1. 必须严格回应用户额外任务，不能忽略；
2. 不要重复第一阶段的故事解说正文；
3. 如果用户要求文章风格分析，就分析原文的叙事方式、语言风格、氛围营造、表达特点；
4. 如果用户要求人物性格分析，就分析原文中出现的主要人物性格，并结合事件说明；
5. 如果用户要求主题、结构、写法、人物关系等，也必须单独回应；
6. 分析必须基于 PDF 原文和已经生成的解说，不要编造原文外信息；
7. 可以使用简短小标题，例如“文章风格分析”“人物性格分析”；
8. 输出内容应该是额外任务结果，不要再写一遍故事解说。

现在请直接输出第二个任务的结果。
"""

    def _call_model(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1200,
    ) -> str:
        kwargs = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "你是中文书籍深度解说口播员。"
                        "必须严格根据原文讲述情节。"
                        "不要询问用户要做什么。"
                        "不要写主题总结、读后感或文学升华。"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "top_p": 0.75,
        }

        kwargs["extra_body"] = {
            "options": {
                "repeat_penalty": 1.08,
                "num_predict": max_tokens,
                "num_ctx": 49152,
            }
        }

        try:
            response = self.client.chat.completions.create(**kwargs)
        except TypeError:
            kwargs.pop("extra_body", None)
            response = self.client.chat.completions.create(**kwargs)

        return response.choices[0].message.content or ""

    def _extract_source_text(self, content: str) -> str:
        if not isinstance(content, str):
            return ""

        patterns = [
            r"PDF 指定页码范围内的原文内容：\s*(.*?)(?:\n生成要求：|\Z)",
            r"PDF 原文内容：\s*(.*?)(?:\n生成要求：|\Z)",
            r"书籍原文内容：\s*(.*?)(?:\n生成要求：|\Z)",
            r"【原文内容】\s*(.*?)(?:\n【|\Z)",
            r"PDF 原文：\s*(.*?)(?:\n现在直接输出|\Z)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content, re.S)
            if match:
                return match.group(1).strip()

        return content.strip()

    def _clean_output(self, text: str) -> str:
        if not text:
            return ""

        text = str(text)

        remove_phrases = [
            "以下是深度阅读正文：",
            "以下是正文：",
            "深度阅读正文：",
            "正文：",
            "故事梗概",
            "主题分析",
            "读后感",
            "文学升华",
        ]

        for phrase in remove_phrases:
            text = text.replace(phrase, "")

        text = text.replace("\\n", "\n")
        text = re.sub(r"[*#•]", "", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()

        return text

    def _save_debug_prompt(self, prompt: str, style: str, reading_mode: str) -> None:
        try:
            debug_dir = Path("debug_prompts")
            debug_dir.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_style = re.sub(r"[^\w\u4e00-\u9fff-]", "_", style or "style")
            path = debug_dir / f"{ts}_{safe_style}_{reading_mode}.txt"
            path.write_text(prompt, encoding="utf-8")
            print("========== GEMMA_DEBUG_PROMPT_SAVED ==========")
            print(str(path.resolve()))
        except Exception as e:
            print("保存 debug prompt 失败：", e)
