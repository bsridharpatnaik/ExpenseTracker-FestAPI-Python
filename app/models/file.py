from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from app.database import Base
from datetime import datetime

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True, index=True)
    file_uuid = Column(String(36), unique=True, index=True)
    filename = Column(String(255))
    file_data = Column(LargeBinary(length=(2**32)-1))
    upload_date = Column(DateTime, default=datetime.utcnow)