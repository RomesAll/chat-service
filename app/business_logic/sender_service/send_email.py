import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pydantic import SecretStr
from app.shared.log_config import LogMixin
from app.shared.config import config

class EmailSender(LogMixin):
    def __init__(self, smtp_server: str, port: int, sender_email: str, password: SecretStr):
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email
        self.password = password

    def send_message(self, to: str, msg_send: str):
        # Создаем контейнер для сообщения
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = to
        msg['Subject'] = 'Код подтверждения для входа в приложение чата'

        # Добавляем текст письма
        mime_type = 'plain'
        msg.attach(MIMEText(msg_send, mime_type, 'utf-8'))

        try:
            # Подключаемся к SMTP-серверу и отправляем письмо
            if self.port == 465:
                # SSL подключение
                with smtplib.SMTP_SSL(self.smtp_server, self.port) as server:
                    server.login(self.sender_email, self.password.get_secret_value())
                    server.send_message(msg)
            else:
                # TLS подключение (порт 587 и другие)
                with smtplib.SMTP(self.smtp_server, self.port) as server:
                    server.starttls()
                    server.login(self.sender_email, self.password.get_secret_value())
                    server.send_message(msg)
            self.log_info(f"Письмо успешно отправлено пользователю по email {to}")
            return True
        except Exception as e:
            self.log_error(f"Ошибка при отправке: {e}")
            return False
