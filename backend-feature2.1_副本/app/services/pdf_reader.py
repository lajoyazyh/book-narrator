# app/services/pdf_reader.py

import re
from pathlib import Path

import fitz


def get_pdf_page_count(pdf_path: str) -> int:
    """
    获取 PDF 总页数。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    doc = fitz.open(pdf_path)

    try:
        return len(doc)
    finally:
        doc.close()


def get_pdf_text_by_page(pdf_path: str, page_number: int) -> str:
    """
    获取某一页文本，page_number 从 1 开始。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    doc = fitz.open(pdf_path)

    try:
        if page_number < 1 or page_number > len(doc):
            return ""

        page = doc[page_number - 1]
        return page.get_text("text") or ""
    finally:
        doc.close()


def is_catalog_or_front_page(text: str) -> bool:
    """
    判断是否为目录页、简介页、作者简介页、前言页等非正文页面。
    """
    if not text:
        return False

    compact = text.replace(" ", "").replace("\n", "")

    front_keywords = [
        "目录",
        "内容简介",
        "作者简介",
        "前言",
        "序言",
        "出版说明",
        "版权",
        "目录内容简介",
    ]

    keyword_hits = sum(1 for kw in front_keywords if kw in compact)

    chapter_hits = len(
        re.findall(r"第[一二三四五六七八九十百千万零〇\d]+章", compact)
    )

    # 目录页常见特征：有“目录”，并且一页里出现多个章节名
    if "目录" in compact and chapter_hits >= 2:
        return True

    # 内容简介/作者简介/前言一般不是正文
    if keyword_hits >= 1 and len(compact) < 2000:
        return True

    return False


def detect_chapters_from_bookmarks(pdf_path: str) -> list[dict]:
    """
    优先使用 PDF 自带书签目录识别章节。
    这是最可靠的方式。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    doc = fitz.open(pdf_path)
    chapters = []

    try:
        total_pages = len(doc)
        toc = doc.get_toc(simple=True)

        if not toc:
            return []

        # toc item: [level, title, page]
        raw_chapters = []

        for level, title, page in toc:
            title = str(title).strip()

            if not title:
                continue

            # 只取比较像章节的条目
            if is_chapter_title(title):
                if page < 1 or page > total_pages:
                    continue

                raw_chapters.append(
                    {
                        "title": title,
                        "start_page": page,
                    }
                )

        if not raw_chapters:
            return []

        for index, item in enumerate(raw_chapters):
            start_page = item["start_page"]

            if index < len(raw_chapters) - 1:
                end_page = max(start_page, raw_chapters[index + 1]["start_page"] - 1)
            else:
                end_page = total_pages

            chapters.append(
                {
                    "chapter_number": index + 1,
                    "title": item["title"],
                    "start_page": start_page,
                    "end_page": end_page,
                    "source": "bookmark",
                }
            )

        return chapters

    finally:
        doc.close()


def detect_chapters_from_pdf(
        pdf_path: str,
        max_scan_pages: int = 150,
) -> list[dict]:
    """
    尝试从 PDF 正文中识别真实章节。

    注意：
    - 会跳过目录页，防止把目录中的“第一章、第二章、第三章”识别成正文页。
    - 优先返回真实正文页中的章节标题。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    # 1. 优先用 PDF 书签
    bookmark_chapters = detect_chapters_from_bookmarks(pdf_path)
    if bookmark_chapters:
        return bookmark_chapters

    doc = fitz.open(pdf_path)
    chapters = []

    try:
        total_pages = len(doc)
        scan_pages = min(total_pages, max_scan_pages)

        seen_titles = set()

        for page_index in range(scan_pages):
            page_number = page_index + 1
            page = doc[page_index]
            text = page.get_text("text") or ""

            # 2. 跳过目录/简介/前言等页面
            if is_catalog_or_front_page(text):
                continue

            lines = [line.strip() for line in text.splitlines() if line.strip()]

            for line_index, line in enumerate(lines):
                if len(line) > 60:
                    continue

                if not is_chapter_title(line):
                    continue

                normalized_title = line.replace(" ", "")

                if normalized_title in seen_titles:
                    continue

                # 3. 标题附近必须不像目录
                # 如果同一页有很多章节标题，仍可能是目录页，跳过
                chapter_like_count_on_page = sum(
                    1 for candidate in lines if is_chapter_title(candidate)
                )

                if chapter_like_count_on_page >= 3:
                    continue

                seen_titles.add(normalized_title)

                chapters.append(
                    {
                        "chapter_number": len(chapters) + 1,
                        "title": line,
                        "start_page": page_number,
                        "end_page": total_pages,
                        "source": "detected",
                    }
                )

        for i in range(len(chapters)):
            if i < len(chapters) - 1:
                chapters[i]["end_page"] = max(
                    chapters[i]["start_page"],
                    chapters[i + 1]["start_page"] - 1,
                    )
            else:
                chapters[i]["end_page"] = total_pages

        if len(chapters) > 50:
            return []

        return chapters

    finally:
        doc.close()


def is_chapter_title(line: str) -> bool:
    """
    判断一行是否像章节标题。
    """
    if not line:
        return False

    text = line.strip()

    patterns = [
        r"^第\s*[一二三四五六七八九十百千万零〇\d]+\s*章.{0,40}$",
        r"^第\s*[一二三四五六七八九十百千万零〇\d]+\s*回.{0,40}$",
        r"^Chapter\s+\d+[:：\s]?.{0,50}$",
        r"^CHAPTER\s+\d+[:：\s]?.{0,50}$",
    ]

    return any(re.match(pattern, text, re.IGNORECASE) for pattern in patterns)


def find_likely_body_start_page(pdf_path: str) -> int:
    """
    粗略寻找正文开始页。
    用于无法识别章节时，避免分页片段从封面/目录开始。
    """
    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    doc = fitz.open(pdf_path)

    try:
        total_pages = len(doc)
        scan_pages = min(total_pages, 30)

        for page_index in range(scan_pages):
            page_number = page_index + 1
            text = doc[page_index].get_text("text") or ""
            compact = text.replace(" ", "").replace("\n", "")

            if not compact:
                continue

            if is_catalog_or_front_page(text):
                continue

            # 明确章节标题，通常是正文开始
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if any(is_chapter_title(line) for line in lines):
                return page_number

            # 如果这一页文字足够多，且不像目录页，也可认为是正文
            if len(compact) > 300:
                return page_number

        return 1

    finally:
        doc.close()


def build_page_chunks(
        total_pages: int,
        chunk_size: int = 5,
        start_page: int = 1,
) -> list[dict]:
    """
    如果无法识别真实章节，则按页数生成“分页片段”。
    注意：这里叫分页片段，不叫真实章节。
    """
    chapters = []

    if total_pages <= 0:
        return chapters

    chapter_number = 1
    start = max(1, start_page)

    while start <= total_pages:
        end = min(total_pages, start + chunk_size - 1)

        chapters.append(
            {
                "chapter_number": chapter_number,
                "title": f"分页片段：第 {start}-{end} 页",
                "start_page": start,
                "end_page": end,
                "source": "page_chunk",
            }
        )

        chapter_number += 1
        start = end + 1

    return chapters