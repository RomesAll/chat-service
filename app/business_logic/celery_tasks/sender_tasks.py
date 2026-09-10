from app.business_logic.sender_service import ISender
from app.shared.celery_app import app
from app.business_logic.sender_service.send_email import EmailSender
from app.business_logic.sender_service.phone import SMSSender
from app.shared.config import config
from app.shared.dtos.auth import SendType


def _make_sender(sender_type: SendType) -> ISender:
    if sender_type == SendType.EMAIL:
        return EmailSender(
            smtp_server=config.smtp.server,
            port=config.smtp.port,
            sender_email=config.smtp.gmail,
            password=config.smtp.app_psw,
        )
    elif sender_type == SendType.PHONE:
        return SMSSender(
            api_token_id=config.sms.api_token_id
        )
    raise Exception


@app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,), # авто-retry на любую ошибку
    retry_backoff=True,
    retry_jitter=True,
)
def send_message(self, to: str, msg: str, send_type: SendType):
    sender = _make_sender(send_type)
    ok = sender.send_message(to=to, msg_send=msg)
    if not ok:
        raise RuntimeError(f"Не удалось отправить письмо на {to}")
    return {"to": to, "status": "sent"}