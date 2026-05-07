import logging
from datetime import datetime
from typing import List, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

from app.AI.memory import ConversationMemory
from app.AI.prompts.system_prompt import load_system_prompt
from app.AI.tools import get_tools
from app.core.settings import settings
from app.loader.database import sessionmanager
from app.modules.cache import CacheService

logger = logging.getLogger("chatbot")


class ChatbotService:
    """Singleton service điều phối LangChain Agent và ConversationMemory."""

    def __init__(self):
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.7,
            google_api_key=settings.GOOGLE_API_KEY,
        )

        # Initialize tools
        self.tools = get_tools()

        # Load system prompt
        self.system_prompt = load_system_prompt()

        # Build ReAct agent prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create ReAct agent + executor
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        # Initialize memory
        self.memory = ConversationMemory(
            cache_service=CacheService(),
            db_session_factory=sessionmanager.get_session,
        )

    async def chat(self, message: str, user_id: str) -> dict:
        """
        Xử lý tin nhắn từ người dùng.
        Returns: {"response": str, "success": bool, "tools_used": list, "user_id": str}
        """
        try:
            # Load conversation history
            chat_history = await self.memory.load_history(user_id)

            # Invoke agent
            result = await self.agent_executor.ainvoke(
                {"input": message, "chat_history": chat_history}
            )

            response_text = result.get("output", "")

            # Extract tools_used from intermediate steps
            tools_used = []
            intermediate_steps = result.get("intermediate_steps", [])
            for step in intermediate_steps:
                if isinstance(step, tuple) and len(step) >= 1:
                    action = step[0]
                    tool_name = getattr(action, "tool", None)
                    if tool_name and tool_name not in tools_used:
                        tools_used.append(tool_name)

            # Save message pair to memory
            await self.memory.save_message_pair(user_id, message, response_text)

            return {
                "response": response_text,
                "success": True,
                "tools_used": tools_used,
                "user_id": user_id,
            }

        except Exception as e:
            logger.error(
                "Chatbot error",
                extra={
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat(),
                },
            )
            return {
                "response": f"Xin lỗi, đã xảy ra lỗi: {type(e).__name__}",
                "success": False,
                "error": str(e),
                "tools_used": [],
                "user_id": user_id,
            }

    async def clear_memory(self, user_id: str) -> None:
        """Xóa bộ nhớ hội thoại của user khỏi Redis và PostgreSQL."""
        await self.memory.clear(user_id)

    async def get_conversation_history(self, user_id: str) -> List[dict]:
        """
        Trả về lịch sử hội thoại từ PostgreSQL.
        Returns: [{"role": "user"|"assistant", "content": str}, ...]
        """
        return await self.memory.get_full_history(user_id)


# Singleton instance
_chatbot_instance: Optional[ChatbotService] = None


def get_chatbot() -> ChatbotService:
    """Factory function trả về singleton ChatbotService."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = ChatbotService()
    return _chatbot_instance
