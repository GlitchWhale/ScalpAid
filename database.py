from sqlalchemy import create_engine, Column, Integer, String, Float, BigInteger, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from config import SQLALCHEMY_URL

Base = declarative_base()
engine = create_engine(SQLALCHEMY_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    email = Column(String(190), unique=True, nullable=False)
    hair_type = Column(String(50))
    purpose = Column(String(255))
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, autoincrement=True)
    device = Column(String(50), nullable=False)
    sensor_type = Column(String(20), nullable=False)
    value = Column(Float, nullable=False)
    state = Column(String(20))
    timestamp = Column(BigInteger, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)
