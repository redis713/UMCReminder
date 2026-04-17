import os

class Config:
    SECRET_KEY = 'aaaa'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://user:pass@localhost/reminder"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your-telegram-bot-token")
    #TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "your-chat-id")