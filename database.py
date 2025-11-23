from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from config import SQLALCHEMY_URL, fernet

Base = declarative_base()
engine = create_engine(SQLALCHEMY_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=True)
    email = Column(String(190), unique=True, nullable=False)
    hair_type = Column(String(50), nullable=True)
    purpose = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    google_id = Column(String(255), unique=True, nullable=True)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), nullable=False)
    moisture_cipher = Column(String(512), nullable=False)
    temperature_cipher = Column(String(512), nullable=False)
    moisture_unit = Column(String(16), nullable=False, default="%")
    temperature_unit = Column(String(16), nullable=False, default="C")
    created_at = Column(DateTime, server_default=func.now())
    timestamp = Column(Integer, nullable=True)

    def set_moisture(self, value: str):
        self.moisture_cipher = fernet.encrypt(value.encode()).decode()

    def get_moisture(self) -> str:
        return fernet.decrypt(self.moisture_cipher.encode()).decode()

    def set_temperature(self, value: str):
        self.temperature_cipher = fernet.encrypt(value.encode()).decode()

    def get_temperature(self) -> str:
        return fernet.decrypt(self.temperature_cipher.encode()).decode()


def init_db():
    Base.metadata.create_all(bind=engine)
