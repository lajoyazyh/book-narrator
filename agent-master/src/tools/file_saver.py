# src/tools/file_saver.py

"""
文件保存工具 - 将解说词保存到文本文件
"""
from pathlib import Path
from typing import Optional

class FileSaver:
    """文件保存工具"""
    
    def __init__(self, output_dir: str = "output/scripts"):
        """
        初始化文件保存器
        
        Args:
            output_dir: 输出目录，默认 output/scripts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, content: str, filename: str) -> str:
        """
        保存文件工具
        
        Args:
            content: 要保存的文本内容
            filename: 文件名
            
        Returns:
            保存的文件路径
        """
        # 1. 如果文件名包含路径，只取最后一部分
        if '/' in filename or '\\' in filename:
            filename = Path(filename).name
            print(f"文件名已清理: {filename}")
        
        # 2. 构建完整路径
        filepath = self.output_dir / filename

        # 保存前打印
        print(f"\n正在保存文件: {filename}")
        print(f"   内容长度: {len(content)} 字符")
    
        # 3. 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"文件已保存: {filepath}")
        
        return str(filepath)