import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = os.getenv("SMTP_PORT", 587)
SMTP_USER = os.getenv("SMTP_USER", "univesp.proj@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "hxeg gxnx ljpi mupq")

SMTP_CONFIG = {
    "host": "smtp.gmail.com",  # Para Gmail
    "port": 465,
    "user": "univesp.proj@gmail.com",
    "password": "hxeg gxnx ljpi mupq"  # Use App Password se tiver 2FA
}
