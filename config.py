import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "scalpaid"),
    "port": int(os.getenv("DB_PORT", 3306))  # optional, must be int
}
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
API_KEY = os.getenv("API_KEY")

fernet = Fernet(ENCRYPTION_KEY.encode())

SQLALCHEMY_URL = (
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
SECRET_KEY = os.getenv("SECRET_KEY")