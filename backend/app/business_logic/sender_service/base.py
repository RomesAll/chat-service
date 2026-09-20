from typing import Protocol


class ISender(Protocol):
    """Класс интерфейс для отправки сообщений"""
    def send_message(self, to: str, msg_send: str):
        """Отправка сообщения клиенту"""
        pass