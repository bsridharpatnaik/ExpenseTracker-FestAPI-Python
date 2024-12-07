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
    
class DailySummary(BaseModel):
    date: str
    carryForward: float
    totalIncome: float
    totalExpense: float
    incomeTransactions: List[TransactionResponse]
    expenseTransactions: List[TransactionResponse]
    balance: float

class GroupedDashboardSummary(BaseModel):
    carryForward: float
    totalIncome: float
    totalExpense: float
    balance: float
    dailySummaries: List[DailySummary]