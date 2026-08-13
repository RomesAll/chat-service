from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from business_logic.active_session.active_session_manager import ActiveSessionManager


class IUseCase(ABC):
    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        pass