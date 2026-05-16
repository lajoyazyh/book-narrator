# config/paths.py
import os # 引入Python的os模块，提供操作系统相关的功能，用来处理文件和目录路径
from pathlib import Path

class PathConfig:
    "路径配置"

    # 根目录
    ROOT_DIR = Path(__file__).parent.parent.parent
    
    #数据路径
    DATA_DIR = ROOT_DIR / "data"  
    BOOKS_DIR = ROOT_DIR / "books"
    OUTPUT_DIR = ROOT_DIR / "output"
    LOGS_DIR = ROOT_DIR / "logs"

    #输出子目录
    AUDIO_DIR = OUTPUT_DIR / "audio"
    SCRIPTS_DIR = OUTPUT_DIR / "scripts"

    @classmethod
    def setup(cls):
        "创建所有必要的目录"
        dirs = [
            cls.DATA_DIR,
            cls.BOOKS_DIR,
            cls.OUTPUT_DIR,
            cls.LOGS_DIR,
            cls.AUDIO_DIR,
            cls.SCRIPTS_DIR
        ]

        for dir_path in dirs:
            dir_path.mkdir(parents=True,exist_ok=True)

    @classmethod
    def get_book_path(cls,filename:str=None) -> Path:
        "获取书籍文件路径"
        return cls.BOOKS_DIR / filename
    
    @classmethod
    def get_audio_path(cls,filename:str)->Path:
        "获取音频文件路径"
        import time
        if filename:
            return cls.AUDIO_DIR / filename    # 这里就是如果提供了指定的名字，那就使用指定的名字，如果没有提供名字，就使用时间戳自动命名。
        timestamp = int(time.time())
        return cls.AUDIO_DIR / f"narration_{timestamp}.mp3"
