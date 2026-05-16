"""
统一日志输出模块 - 专门处理 Agent 任务执行过程中的输出
"""
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List


class AgentLogger:
    """Agent 任务日志记录器"""
    
    # 日志级别
    LEVEL_INFO = "INFO"
    LEVEL_SUCCESS = "SUCCESS"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_STEP = "STEP"
    
    # 颜色码（Windows Terminal 支持）
    COLORS = {
        LEVEL_INFO: "\033[94m",     # 蓝色
        LEVEL_SUCCESS: "\033[92m",  # 绿色
        LEVEL_WARNING: "\033[93m",  # 黄色
        LEVEL_ERROR: "\033[91m",     # 红色
        LEVEL_STEP: "\033[96m",     # 青色
    }
    RESET = "\033[0m"
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color
        self._indent_level = 0
    
    def _format_time(self) -> str:
        """格式化时间戳"""
        return datetime.now().strftime("%H:%M:%S")
    
    def _print(self, level: str, message: str, indent: bool = True):
        """内部打印方法"""
        color = self.COLORS.get(level, "") if self.use_color else ""
        reset = self.RESET if self.use_color else ""
        
        prefix = "  " * self._indent_level if indent else ""
        time_str = f"[{self._format_time()}]"
        
        print(f"{color}{time_str} {prefix}{message}{reset}")
    
    # ================== 任务步骤相关 ==================#
    
    def task_start(self, task_name: str, description: str = ""):
        """开始一个任务"""
        msg = f">>> {task_name}"
        if description:
            msg += f" - {description}"
        self._print(self.LEVEL_STEP, msg)
        self._indent_level += 1
    
    def task_step(self, step_name: str, details: str = ""):
        """输出任务步骤（规划步骤）"""
        msg = f"- {step_name}"
        if details:
            msg += f": {details}"
        self._print(self.LEVEL_STEP, msg)
    
    def task_complete(self, task_name: str, result: str = ""):
        """完成任务"""
        self._indent_level = max(0, self._indent_level - 1)
        msg = f"[完成] {task_name}"
        if result:
            msg += f" -> {result}"
        self._print(self.LEVEL_SUCCESS, msg)
    
    # ================== 具体操作结果 ==================#
    
    def book_loaded(self, book_title: str, author: str = "", total_chapters: int = 0):
        """书籍加载完成"""
        msg = f"书籍已加载: 《{book_title}》"
        if author:
            msg += f" (作者: {author})"
        if total_chapters > 0:
            msg += f", 共 {total_chapters} 章"
        self._print(self.LEVEL_SUCCESS, msg)
    
    def chapters_split(self, total: int, details: List[str] = None):
        """章节分割完成"""
        msg = f"已分割 {total} 章"
        self._print(self.LEVEL_SUCCESS, msg)
        if details:
            for d in details[:5]:  # 只显示前5个
                self._print(self.LEVEL_INFO, f"    - {d}", indent=False)
            if len(details) > 5:
                self._print(self.LEVEL_INFO, f"    ... 还有 {len(details)-5} 章", indent=False)
    
    def narration_generated(self, chapter_number: int, title: str = "", 
                          char_count: int = 0, style: str = ""):
        """解说词生成完成"""
        msg = f"第{chapter_number}章"
        if title:
            msg += f"《{title}》"
        msg += " 解说词已生成"
        if char_count > 0:
            msg += f", {char_count} 字符"
        if style:
            msg += f" (风格: {style})"
        self._print(self.LEVEL_SUCCESS, msg)
    
    def audio_generated(self, chapter_number: int, audio_path: str):
        """音频生成完成"""
        msg = f"第{chapter_number}章 音频已生成"
        self._print(self.LEVEL_SUCCESS, msg)
        self._print(self.LEVEL_INFO, f"    {audio_path}", indent=False)
    
    def file_saved(self, file_path: str, description: str = ""):
        """文件保存完成"""
        msg = f"文件已保存: {file_path}"
        if description:
            msg += f" ({description})"
        self._print(self.LEVEL_SUCCESS, msg)
    
    # ================== 通用信息 ==================#
    
    def info(self, message: str):
        """一般信息"""
        self._print(self.LEVEL_INFO, message)
    
    def warning(self, message: str):
        """警告信息"""
        self._print(self.LEVEL_WARNING, message)
    
    def error(self, message: str):
        """错误信息"""
        self._print(self.LEVEL_ERROR, message)
    
    def section(self, title: str):
        """分段标题"""
        print()
        print("=" * 50)
        print(f"  {title}")
        print("=" * 50)
        print()
    
    def progress(self, current: int, total: int, item_name: str = "项目"):
        """进度信息"""
        msg = f"进度: {current}/{total} {item_name}"
        self._print(self.LEVEL_INFO, msg)
    # ================== Agent 步骤解析 ==================#
    
    def log_agent_steps(self, messages: list):
        """从 messages 中提取并打印 Agent 的规划步骤"""
        ai_count = 0
        for i, msg in enumerate(messages):
            if not isinstance(msg, dict):
                continue
            
            msg_type = msg.get("type", "")
            content = msg.get("content", "")
            
            # 跳过空内容
            if not content:
                continue
            
            # 工具执行结果
            if msg_type == "tool":
                preview = content[:80] + "..." if len(content) > 80 else content
                self.info(f"[Tool] {preview}")
            
            # AI 思考/规划内容 (ai 或 assistant 类型)
            elif msg_type in ("ai", "assistant", "system") or isinstance(content, str):
                ai_count += 1
                preview = content[:150] + "..." if len(content) > 150 else content
                self.task_step(f"思考 {ai_count}", preview)
            
            # 其他类型
            else:
                preview = str(content)[:80]
                self.info(f"[{msg_type}] {preview}")

# ============ 全局单例 ============#
_logger: Optional[AgentLogger] = None

def get_logger() -> AgentLogger:
    """获取全局 logger 实例"""
    global _logger
    if _logger is None:
        _logger = AgentLogger()
    return _logger

# ============ 便捷函数 ============#
def log_task_start(task_name: str, description: str = ""):
    get_logger().task_start(task_name, description)

def log_task_step(step_name: str, details: str = ""):
    get_logger().task_step(step_name, details)

def log_task_complete(task_name: str, result: str = ""):
    get_logger().task_complete(task_name, result)

def log_book_loaded(book_title: str, author: str = "", total_chapters: int = 0):
    get_logger().book_loaded(book_title, author, total_chapters)

def log_chapters_split(total: int, details: List[str] = None):
    get_logger().chapters_split(total, details)

def log_narration_generated(chapter_number: int, title: str = "", 
                           char_count: int = 0, style: str = ""):
    get_logger().narration_generated(chapter_number, title, char_count, style)

def log_audio_generated(chapter_number: int, audio_path: str):
    get_logger().audio_generated(chapter_number, audio_path)

def log_file_saved(file_path: str, description: str = ""):
    get_logger().file_saved(file_path, description)

def log_info(message: str):
    get_logger().info(message)

def log_warning(message: str):
    get_logger().warning(message)

def log_error(message: str):
    get_logger().error(message)

def log_section(title: str):
    get_logger().section(title)

def log_progress(current: int, total: int, item_name: str = "项目"):
    get_logger().progress(current, total, item_name)

def log_agent_steps(messages: list):
    """全局方法：从 messages 中提取 Agent 规划步骤"""
    get_logger().log_agent_steps(messages)