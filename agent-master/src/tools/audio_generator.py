# src/tools/audio_generator.py

'''
音频生成工具 - 将解说词转换为MP3音频
这里使用微软 Edge TTS
'''

import asyncio
from pathlib import Path

import edge_tts
from src.utils.logger import log_info

class AudioGenerator:
    """音频生成器 - 将文本转换为语音"""
    
    # 常用中文语音
    VOICES = {
        "晓晓": "zh-CN-XiaoxiaoNeural",  # 女声，温暖，推荐
        "云希": "zh-CN-YunxiNeural",     # 男声，活力
        "云扬": "zh-CN-YunyangNeural",   # 男声，专业
        "晓伊": "zh-CN-XiaoyiNeural",    # 女声，活泼
    }

    def __init__(self, voice:str = "晓晓"):
        
        self.voice = self.VOICES.get(voice, "zh-CN-XiaoxiaoNeural")
        
        # 创建输出目录
        self.output_dir = Path("output") / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def _generate_async(self, text: str, output_path: str):
        """异步生成音频"""
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)

    def generate(self, text: str, filename: str) -> str:
        """
        生成音频文件
        
        Args:
            text: 要转换的文本
            filename: 原始文件名（如 "三体_第1章.txt"）
            
        Returns:
            生成的音频文件路径
        """
        # 生成音频文件名（把.txt换成.mp3）
        audio_filename = filename.replace('.txt', '.mp3')
        output_path = self.output_dir / audio_filename
        
        log_info(f"正在生成音频: {audio_filename}")
        
        # Edge TTS是异步的，需要这样包装
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self._generate_async(text, str(output_path))
            )
        finally:
            loop.close()
        
        log_info(f"音频生成完成: {output_path}")
        return str(output_path)
    
    def batch_generate(self, narrations: list, book_title: str) -> list:
        """
        批量生成音频
        
        Args:
            narrations: 解说词列表，每个元素是 {"chapter_number": 1, "content": "..."}
            book_title: 书名
            
        Returns:
            生成的音频文件路径列表
        """
        # 处理书名，移除非法字符
        safe_title = "".join(c for c in book_title if c.isalnum() or c in ' _-')
        
        audio_files = []
        for n in narrations:
            filename = f"{safe_title}_第{n['chapter_number']}章.txt"
            audio_file = self.generate(n['content'], filename)
            audio_files.append(audio_file)
        
        return audio_files