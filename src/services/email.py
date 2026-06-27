import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr
from pathlib import Path

from src.conf.config import settings
from src.services.auth import auth_service

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token(data={"sub": email})

        # Read HTML template
        template_path = Path(settings.BASE_DIR) / "src" / "services" / "template" / "email_template.html"
        with open(template_path, "r", encoding="utf-8") as file:
            html_template = file.read()

        # Replace template variables
        html_body = html_template.replace("{{host}}", host)
        html_body = html_body.replace("{{username}}", username)
        html_body = html_body.replace("{{token}}", token_verification)

        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.mail_from
        message["To"] = email
        message["Subject"] = "Confirm your email"

        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.mail_server,
            port=settings.mail_port,
            start_tls=False,
            use_tls=True,
            username=settings.mail_username,
            password=settings.mail_password,
        )

        print(f"Email sent successfully to {email}")

    except Exception as err:
        print(f"Failed to send email: {err}")