from typing import List

from langchain_core.tools import BaseTool

from app.AI.tools.calculator_tool import calculate
from app.AI.tools.time_tool import get_current_time


def get_tools() -> List[BaseTool]:
    """Trả về danh sách tất cả tools đã đăng ký."""
    return [get_current_time, calculate]
