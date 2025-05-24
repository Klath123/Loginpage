from typing import List
from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from src.config import Config


class EmailSchema(BaseModel):
    email: List[EmailStr]

# Configure your SMTP credentials
conf = ConnectionConfig(
    MAIL_USERNAME=Config.MAIL_USERNAME,
    MAIL_PASSWORD=Config.MAIL_PASSWORD,
    MAIL_FROM="keshav.lath11@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_STARTTLS=True,  
    MAIL_SSL_TLS=False,   
    USE_CREDENTIALS=True, 
    VALIDATE_CERTS=True
)


def welcome_email(
    recipient: list,
    html: str,
    subject: str,
    background_tasks: BackgroundTasks
):
    message = MessageSchema(
        subject=subject,
        recipients=recipient,
        body=html,
        subtype=MessageType.html
    )
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)
    # return JSONResponse(status_code=200, content={"message": "Email has been sent"})

