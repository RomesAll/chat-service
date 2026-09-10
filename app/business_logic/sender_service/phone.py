import requests
from pydantic import SecretStr

from app.shared.log_config import LogMixin


class SMSSender(LogMixin):

    def __init__(self, api_token_id: SecretStr):
        """Конструктор класса.

        :param api_token_id: Уникальный API-ключ (токен) от личного кабинета
        SMS.ru
        """
        self.api_id = api_token_id
        self.base_url = "https://sms.ru"

    def send_message(self, to: str, msg_send: str):
        """Метод для отправки одного SMS-сообщения.

        :param to: Номер телефона получателя (например, 79991112233)
        :param msg_send: Текст сообщения
        """
        # Параметры запроса к серверу
        payload = {"api_id": self.api_id.get_secret_value(), "to": to, "msg": msg_send, "json": 1}

        try:
            # Отправляем POST-запрос к API
            response = requests.post(self.base_url, data=payload)
            response.raise_for_status()  # Проверяем на ошибки соединения
            data = response.json()

            # Проверяем статус ответа сервиса
            if data.get("status") == "OK":
                self.log_info(f"Сообщение успешно отправлено на номер {to}")
                return True
            else:
                self.log_warning(f"Ошибка сервиса: {data.get('status_text')}")
                return False

        except Exception as e:
            self.log_error(f"Произошла ошибка при отправке: {e}")
            return False