import logging
import os

logger = logging.getLogger("chatbot")

DEFAULT_SYSTEM_PROMPT: str = """Bạn là một trợ lý văn phòng thông minh. Nhiệm vụ của bạn là hỗ trợ người dùng trong các công việc hàng ngày.

Quy tắc:
- Khi người dùng sử dụng tiếng Việt, hãy trả lời bằng tiếng Việt.
- Trả lời ngắn gọn, rõ ràng và chuyên nghiệp.

Công cụ có sẵn:
- get_current_time: Xem thời gian hiện tại (định dạng YYYY-MM-DD HH:MM:SS).
- calculate: Tính toán biểu thức toán học (hỗ trợ +, -, *, /, **, sqrt, pow, abs, round).

Hãy sử dụng công cụ phù hợp khi người dùng yêu cầu."""

_PROMPT_FILE_PATH = os.path.join(
    os.path.dirname(__file__), "chatbot_prompt.txt"
)


def load_system_prompt() -> str:
    """
    Tải system prompt từ file app/AI/prompts/chatbot_prompt.txt.
    Fallback sang DEFAULT_SYSTEM_PROMPT nếu file không tồn tại.
    """
    try:
        with open(_PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                return content
    except FileNotFoundError:
        logger.warning(
            "System prompt file not found at %s, using default prompt.",
            _PROMPT_FILE_PATH,
        )
    except Exception as e:
        logger.error(
            "Error reading system prompt file: %s. Using default prompt.",
            e,
        )
    return DEFAULT_SYSTEM_PROMPT
