from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_logs import ChatLog


class ChatLogRepository:
    """Repository cho bảng chat_logs."""

    async def create(
        self, db: AsyncSession, user_id: int, message: str, response: str
    ) -> ChatLog:
        chat_log = ChatLog(user_id=user_id, message=message, response=response)
        db.add(chat_log)
        await db.commit()
        await db.refresh(chat_log)
        return chat_log

    async def get_by_user_id(
        self, db: AsyncSession, user_id: int, limit: int = 20
    ) -> List[ChatLog]:
        """Lấy lịch sử theo user_id, sắp xếp theo created_at ASC, giới hạn limit."""
        query = (
            select(ChatLog)
            .where(ChatLog.user_id == user_id)
            .order_by(ChatLog.created_at.asc())
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    async def delete_by_user_id(self, db: AsyncSession, user_id: int) -> None:
        """Xóa toàn bộ chat logs của user."""
        query = delete(ChatLog).where(ChatLog.user_id == user_id)
        await db.execute(query)
        await db.commit()
