import os
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from dotenv import load_dotenv

from my_contacts.services.auth import auth_service


load_dotenv()
user = os.environ.get("MAIL_USERNAME")
password = os.environ.get("MAIL_PASSWORD")
mail_from = os.environ.get("MAIL_FROM")
mail_server = os.environ.get("MAIL_SERVER")

conf = ConnectionConfig(
    MAIL_USERNAME=user,
    MAIL_PASSWORD=password,
    MAIL_FROM=mail_from,
    MAIL_PORT=465,
    MAIL_SERVER=mail_server,
    MAIL_FROM_NAME="Info mail",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email(email_address: EmailStr, username: str, host: str):
    try:
        token_verification = await auth_service.create_email_token({"sub": email_address})
        message = MessageSchema(
            subject="Email address confirmation",
            recipients=[email_address],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
