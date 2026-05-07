import math

from langchain_core.tools import tool

SAFE_FUNCTIONS: dict = {
    "sqrt": math.sqrt,
    "pow": math.pow,
    "abs": abs,
    "round": round,
}

BLOCKED_PATTERNS: list[str] = [
    "import",
    "exec",
    "eval",
    "open",
    "__",
    "os.",
    "sys.",
]


@tool
def calculate(expression: str) -> str:
    """
    Tính toán biểu thức toán học an toàn.
    Hỗ trợ: +, -, *, /, **, sqrt(), pow(), abs(), round()
    Từ chối: biểu thức chứa lệnh hệ thống hoặc truy cập tệp.
    """
    expr_lower = expression.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in expr_lower:
            return f"Lỗi: Biểu thức không an toàn. Phát hiện pattern bị chặn: '{pattern}'"

    try:
        result = eval(expression, {"__builtins__": {}}, SAFE_FUNCTIONS)
        return str(result)
    except ZeroDivisionError:
        return "Lỗi: Phép chia cho 0."
    except Exception as e:
        return f"Lỗi: Không thể tính toán biểu thức '{expression}'. Chi tiết: {e}"
