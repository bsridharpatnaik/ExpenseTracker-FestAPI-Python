from typing import List, Dict
from pydantic import BaseModel
from .transaction import TransactionResponse

class DashboardSummary(BaseModel):
    transactionsByType: Dict[str, List[TransactionResponse]]
    carryForward: float
    totalIncome: float
    totalExpense: float
    balance: float
    username: str