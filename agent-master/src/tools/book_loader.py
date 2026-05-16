# src/tools/book_loader.py

import os
from pathlib import Path
from typing import Optional

import fitz


def get_shared_books_dir() -> Path:
    """
    获取 shared/books 共享目录。
    后端和 Agent 统一使用：
    ~/Desktop/shared/books
    """
    return Path(
        os.getenv("SHARED_BOOKS_DIR", Path.home() / "Desktop" / "shared" / "books")
    ).resolve()


def resolve_book_path(file_path: str) -> str:
    """
    兼容本地 Mac 传来的绝对路径。
    如果原路径在云服务器不存在，就取文件名，到 SHARED_BOOKS_DIR 里找。
    """
    import os
    from pathlib import Path

    raw_path = Path(file_path)

    # 1. 如果传入路径在当前机器存在，直接使用
    if raw_path.exists():
        return str(raw_path)

    # 2. 如果是 Mac 本地绝对路径，云服务器肯定找不到；
    #    这里取文件名，到共享目录里找
    filename = raw_path.name

    shared_dir = os.getenv("SHARED_BOOKS_DIR", "../shared/books")
    shared_path = Path(shared_dir)

    if not shared_path.is_absolute():
        shared_path = Path.cwd() / shared_path

    candidate = shared_path / filename

    if candidate.exists():
        return str(candidate)

    # 3. 兼容后端上传后文件名带 book_id 前缀的情况
    #    例如前端传 my_book.pdf，但云端实际是 eeadece1_my_book.pdf
    for pdf in shared_path.glob("*.pdf"):
        if pdf.name == filename:
            return str(pdf)

        if pdf.name.endswith("_" + filename):
            return str(pdf)

    raise FileNotFoundError(
        f"PDF 文件不存在：{file_path}；也未在共享目录找到：{candidate}"
    )

def get_pdf_page_count(file_path: str) -> int:
    pdf_path = resolve_book_path(file_path)
    doc = fitz.open(pdf_path)

    try:
        return len(doc)
    finally:
        doc.close()


def normalize_page_text(text: str) -> str:
    if not text:
        return ""

    lines = [line.rstrip() for line in text.splitlines()]
    cleaned_lines = []

    previous_blank = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
            continue

        cleaned_lines.append(stripped)
        previous_blank = False

    return "\n".join(cleaned_lines).strip()


def extract_pdf_text(
    file_path: str,
    start_page: int = 1,
    end_page: int = 3,
    max_chars: Optional[int] = None,
    per_page_max_chars: Optional[int] = None,
) -> str:
    """
    从 PDF 指定页码范围提取文本。
    不做摘要，只读取原文。
    """
    pdf_path = resolve_book_path(file_path)
    doc = fitz.open(pdf_path)

    try:
        total_pages = len(doc)

        start = max(1, int(start_page))
        end = min(total_pages, int(end_page))

        if start > end:
            raise ValueError("开始页不能大于结束页")

        texts = []
        current_length = 0

        for page_number in range(start, end + 1):
            page = doc[page_number - 1]
            text = page.get_text("text") or ""
            text = normalize_page_text(text)

            if not text:
                continue

            if per_page_max_chars is not None and len(text) > per_page_max_chars:
                text = text[:per_page_max_chars] + "\n……本页内容已截断……"

            page_text = f"\n\n【第 {page_number} 页】\n{text}"
            texts.append(page_text)
            current_length += len(page_text)

            if max_chars is not None and current_length >= max_chars:
                texts.append("\n\n……后续内容已截断……")
                break

        full_text = "\n".join(texts).strip()

        if max_chars is not None:
            return full_text[:max_chars]

        return full_text

    finally:
        doc.close()


def extract_pdf_text_compact(
    file_path: str,
    start_page: int = 1,
    end_page: int = 3,
    max_chars: Optional[int] = None,
    per_page_max_chars: Optional[int] = None,
) -> str:
    """
    兼容旧代码。
    不再做“摘要抽取”，直接读取原文。
    """
    return extract_pdf_text(
        file_path=file_path,
        start_page=start_page,
        end_page=end_page,
        max_chars=max_chars,
        per_page_max_chars=per_page_max_chars,
    )


class BookLoader:
    def load(
        self,
        file_path: str,
        start_page: int = 1,
        end_page: int = 3,
    ) -> str:
        return extract_pdf_text(
            file_path=file_path,
            start_page=start_page,
            end_page=end_page,
        )


class BookLoaderTool:
    def load_book(
        self,
        file_path: str,
        start_page: int = 1,
        end_page: int = 3,
    ) -> str:
        return extract_pdf_text(
            file_path=file_path,
            start_page=start_page,
            end_page=end_page,
        )