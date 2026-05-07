import json
import logging
from typing import List, Union

from langchain_core.messages import AIMessage, HumanMessage

from app.modules.cache import CacheService
from app.repositories.chat_logs import ChatLogRepository

logger = logging.getLogger("chatbot")


class ConversationMemory:
    """Quản lý lịch sử hội thoại theo user_id với Redis + PostgreSQL."""

    MAX_HISTORY_PAIRS: int = 20

    def __init__(self, cache_service: CacheService, db_session_factory):
        self.cache = cache_service
        self.session_factory = db_session_factory
        self.chat_repo = ChatLogRepository()

    def _redis_key(self, user_id: str) -> str:
        return f"chat:{user_id}"

    def _messages_to_json(self, messages: List[Union[HumanMessage, AIMessage]]) -> str:
        """Convert LangChain messages to JSON string for Redis storage."""
        data = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                data.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                data.append({"role": "assistant", "content": msg.content})
        return json.dumps(data, ensure_ascii=False)

    def _json_to_messages(self, json_str: str) -> List[Union[HumanMessage, AIMessage]]:
        """Convert JSON string from Redis to LangChain messages."""
        data = json.loads(json_str)
        messages = []
        for item in data:
            if item["role"] == "user":
                messages.append(HumanMessage(content=item["content"]))
            elif item["role"] == "assistant":
                messages.append(AIMessage(content=item["content"]))
        return messages

    def _db_records_to_messages(self, records) -> List[Union[HumanMessage, AIMessage]]:
        """Convert ChatLog records to LangChain messages."""
        messages = []
        for record in records:
            messages.append(HumanMessage(content=record.message))
            messages.append(AIMessage(content=record.response))
        return messages

    async def _get_db_session(self):
        """Get a database session from the session factory."""
        session_gen = self.session_factory()
        session = await session_gen.__anext__()
        return session, session_gen

    async def load_history(self, user_id: str) -> List[Union[HumanMessage, AIMessage]]:
        """
        Tải lịch sử hội thoại. Ưu tiên Redis, fallback sang PostgreSQL.
        Returns: List[HumanMessage | AIMessage] (tối đa MAX_HISTORY_PAIRS cặp)
        """
        # Try Redis first
        try:
            cached = self.cache.get(self._redis_key(user_id))
            if cached is not None:
                messages = self._json_to_messages(cached)
                # Limit to MAX_HISTORY_PAIRS pairs (each pair = 2 messages)
                max_messages = self.MAX_HISTORY_PAIRS * 2
                if len(messages) > max_messages:
                    messages = messages[-max_messages:]
                return messages
        except Exception as e:
            logger.warning(
                "Redis error when loading history, falling back to PostgreSQL",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )

        # Fallback to PostgreSQL
        try:
            session, session_gen = await self._get_db_session()
            try:
                records = await self.chat_repo.get_by_user_id(
                    session, int(user_id), limit=self.MAX_HISTORY_PAIRS
                )
                messages = self._db_records_to_messages(records)
                return messages
            finally:
                try:
                    await session_gen.aclose()
                except Exception:
                    pass
        except Exception as e:
            logger.error(
                "PostgreSQL error when loading history",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )
            return []

    async def save_message_pair(self, user_id: str, message: str, response: str) -> None:
        """Lưu cặp tin nhắn-phản hồi vào cả Redis và PostgreSQL."""
        # Save to PostgreSQL
        try:
            session, session_gen = await self._get_db_session()
            try:
                await self.chat_repo.create(session, int(user_id), message, response)
            finally:
                try:
                    await session_gen.aclose()
                except Exception:
                    pass
        except Exception as e:
            logger.error(
                "PostgreSQL error when saving message pair",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )

        # Save to Redis
        try:
            # Load existing history from Redis, append new pair
            existing = []
            try:
                cached = self.cache.get(self._redis_key(user_id))
                if cached is not None:
                    existing = json.loads(cached)
            except Exception:
                pass

            existing.append({"role": "user", "content": message})
            existing.append({"role": "assistant", "content": response})

            # Limit to MAX_HISTORY_PAIRS pairs
            max_items = self.MAX_HISTORY_PAIRS * 2
            if len(existing) > max_items:
                existing = existing[-max_items:]

            self.cache.set(
                self._redis_key(user_id),
                json.dumps(existing, ensure_ascii=False),
                ttl=1800,
            )
        except Exception as e:
            logger.warning(
                "Redis error when saving message pair",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )

    async def clear(self, user_id: str) -> None:
        """Xóa toàn bộ lịch sử của user khỏi Redis và PostgreSQL."""
        # Clear Redis
        try:
            self.cache.delete(self._redis_key(user_id))
        except Exception as e:
            logger.warning(
                "Redis error when clearing history",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )

        # Clear PostgreSQL
        try:
            session, session_gen = await self._get_db_session()
            try:
                await self.chat_repo.delete_by_user_id(session, int(user_id))
            finally:
                try:
                    await session_gen.aclose()
                except Exception:
                    pass
        except Exception as e:
            logger.error(
                "PostgreSQL error when clearing history",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )

    async def get_full_history(self, user_id: str) -> List[dict]:
        """Truy vấn toàn bộ lịch sử từ PostgreSQL theo thứ tự thời gian."""
        try:
            session, session_gen = await self._get_db_session()
            try:
                # Use a large limit to get full history, sorted by created_at ASC
                records = await self.chat_repo.get_by_user_id(
                    session, int(user_id), limit=10000
                )
                history = []
                for record in records:
                    history.append({"role": "user", "content": record.message})
                    history.append({"role": "assistant", "content": record.response})
                return history
            finally:
                try:
                    await session_gen.aclose()
                except Exception:
                    pass
        except Exception as e:
            logger.error(
                "PostgreSQL error when getting full history",
                extra={"error_type": type(e).__name__, "user_id": user_id},
            )
            return []
