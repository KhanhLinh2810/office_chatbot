from datetime import datetime

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Trả về thời gian hiện tại theo định dạng YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
