from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from pydantic import EmailStr

from app.config import settings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

mail_config = ConnectionConfig(
  MAIL_USERNAME=settings.MAIL_USERNAME,
  MAIL_PASSWORD=settings.MAIL_PASSWORD,
  MAIL_FROM=settings.MAIL_FROM,
  MAIL_PORT=587,
  MAIL_SERVER=settings.MAIL_SERVER,
  MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
  MAIL_STARTTLS=True,
  MAIL_SSL_TLS=False,
  USE_CREDENTIALS=True,
  VALIDATE_CERTS=True,
  TEMPLATE_FOLDER=Path(BASE_DIR, "templates"),
)


mail = FastMail(
  config = mail_config
)



def create_message(recipients: list[EmailStr], subject: str, body: str):

  message = MessageSchema(
    subject=subject,
    recipients=recipients,
    body=body,
    subtype=MessageType.html
  )

  return message







