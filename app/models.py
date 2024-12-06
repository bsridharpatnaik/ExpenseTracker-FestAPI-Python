from app.database import Base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    


class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_uuid = Column(String(36), unique=True, index=True)
    filename = Column(String(255))
    file_data = Column(LargeBinary(length=(2**32)-1))  # LONGBLOB for MySQL
    upload_date = Column(DateTime, default=datetime.utcnow)