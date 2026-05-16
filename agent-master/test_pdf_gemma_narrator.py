# test_pdf_gemma_narrator.py

import os
import fitz  # PyMuPDF

from src.tools.narrator import NarratorTool
from src.tools.audio_generator import AudioGenerator


def extract_pdf_text(pdf_path: str, max_pages: int = 5) -> str:
    """
    从 PDF 中提取文本。
    默认只读取前 5 页，避免本地模型处理太慢。
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF 文件不存在：{pdf_path}")

    doc = fitz.open(pdf_path)
    texts = []

    page_count = min(len(doc), max_pages)

    for page_index in range(page_count):
        page = doc[page_index]
        text = page.get_text("text")
        if text.strip():
            texts.append(f"\n\n【第 {page_index + 1} 页】\n{text}")

    doc.close()
    return "\n".join(texts)


def split_text(text: str, chunk_size: int = 2000) -> list[str]:
    """
    把长文本切成多个小片段。
    """
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def main():
    pdf_path = "books/test_book.pdf"

    print("正在读取 PDF...")
    full_text = extract_pdf_text(pdf_path, max_pages=5)

    if not full_text.strip():
        print("PDF 没有提取到文本。可能是扫描版 PDF，需要 OCR。")
        return

    print(f"PDF 文本提取完成，长度：{len(full_text)} 字符")

    chunks = split_text(full_text, chunk_size=2000)
    print(f"文本已切分为 {len(chunks)} 个片段")

    narrator = NarratorTool(style="短视频")

    # 这里可以换声音：晓晓、云希、云扬、晓伊
    audio_generator = AudioGenerator(voice="晓晓")

    all_results = []
    audio_files = []

    for index, chunk in enumerate(chunks, start=1):
        print(f"\n正在生成第 {index}/{len(chunks)} 段解说词...")

        result = narrator.generate(
            content=chunk,
            title="PDF 书籍测试",
            chapter_number=index,
            style="短视频"
        )

        all_results.append(f"\n\n===== 第 {index} 段解说 =====\n\n{result}")

        print(f"第 {index} 段解说词生成完成")

        # 每一段单独生成一个 MP3，避免文本太长导致 TTS 失败
        audio_filename = f"test_book_第{index}段.txt"
        print(f"正在生成第 {index} 段音频...")

        audio_path = audio_generator.generate(
            text=result,
            filename=audio_filename
        )

        audio_files.append(audio_path)
        print(f"第 {index} 段音频生成完成：{audio_path}")

    final_script = "\n".join(all_results)

    script_output_path = "output/scripts/test_book_gemma_narration.txt"
    os.makedirs(os.path.dirname(script_output_path), exist_ok=True)

    with open(script_output_path, "w", encoding="utf-8") as f:
        f.write(final_script)

    print("\n全部生成完成！")
    print(f"解说词已保存到：{script_output_path}")

    print("\n生成的音频文件：")
    for audio_file in audio_files:
        print(audio_file)

    print("\n========== 解说词预览 ==========\n")
    print(final_script[:2000])


if __name__ == "__main__":
    main()