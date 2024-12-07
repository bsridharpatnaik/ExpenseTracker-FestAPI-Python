from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from app.database import Base
from datetime import datetime
from enum import Enum
from typing import List

class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    title = Column(String(255), nullable=False)
    party = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    description = Column(String(500))
    creation_date = Column(DateTime, default=datetime.utcnow)
    modification_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionFile(Base):
    __tablename__ = "transaction_files"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey('transactions.id'))
    file_id = Column(Integer, ForeignKey('files.id'))