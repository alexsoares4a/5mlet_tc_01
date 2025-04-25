import smtplib
from email.mime.text import MIMEText
from config import SMTP_CONFIG  # Vamos criar isso

def send_verification_email(email: str, token: str):
    message = f"""
    Clique no link para verificar sua conta:
    http://localhost:8000/verify-email?token={token}
    
    Ou copie este token manualmente:
    {token}
    """
    
    msg = MIMEText(message)
    msg["Subject"] = "Confirme seu e-mail"
    msg["From"] = SMTP_CONFIG["user"]
    msg["To"] = email

    try:
        with smtplib.SMTP_SSL(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
