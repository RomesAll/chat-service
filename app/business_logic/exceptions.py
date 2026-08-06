from uuid import UUID


class UserConnectionNotFound(Exception):
    """Не удачная попытка поиска подключений пользователя для отправки сообщения"""
    def __init__(self, target_id: UUID):
        message = f'Подключения пользователя {target_id} не найдено'
        super().__init__(message)


class SendMessageError(Exception):
    """Ошибка отправки сообщения"""
    def __init__(self, sender_id: UUID, target_id: UUID, cause: str):
        self.message = (f'Не удалось отправить сообщение '
                        f'пользователю: {target_id} от {sender_id} '
                        f'по причине: {cause}')