from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from datetime import datetime

class FileInfo(BaseModel):
    fileUuid: str
    filename: str
    uploadDate: str
    
class TransactionResponse(BaseModel):
    id: int
    date: str
    creationDate: str
    modificationDate: str
    title: str
    party: str
    amount: float
    transactionType: str
    description: Optional[str]
    fileInfos: List[FileInfo]
    
class TransactionType(str, Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

class FileRequest(BaseModel):
    fileUuid: str

class TransactionRequest(BaseModel):
    transactionType: TransactionType
    date: str
    title: str
    party: str
    amount: Decimal
    description: Optional[str] = None
    files: List[FileRequest] = []
