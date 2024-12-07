from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, File, TransactionFile
from app.auth import get_current_user
from datetime import datetime
from sqlalchemy import func
from typing import Dict, List
from app.schemas import DashboardSummary, GroupedDashboardSummary, DailySummary
from sqlalchemy import case, func

router = APIRouter(prefix="/api/dashboard")

@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    dateOrMonth: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    date = datetime.strptime(dateOrMonth, "%Y-%m-%d")
    
    # Get transactions for the day with files
    transactions = (
        db.query(Transaction)
        .filter(func.date(Transaction.date) == date.date())
        .all()
    )

    total_income = 0
    total_expense = 0
    transactions_by_type = {"INCOME": [], "EXPENSE": []}

    for transaction in transactions:
        files = (
            db.query(File)
            .join(TransactionFile)
            .filter(TransactionFile.transaction_id == transaction.id)
            .all()
        )

        transaction_dict = {
            "id": transaction.id,
            "date": transaction.date.strftime("%d-%m-%Y"),
            "creationDate": transaction.creation_date.strftime("%d-%m-%Y %I:%M:%S %p"),
            "modificationDate": transaction.modification_date.strftime("%d-%m-%Y %I:%M:%S %p"),
            "title": transaction.title,
            "party": transaction.party,
            "amount": float(transaction.amount),
            "transactionType": transaction.transaction_type,
            "description": transaction.description,
            "fileInfos": [
                {
                    "fileUuid": file.file_uuid,
                    "filename": file.filename,
                    "uploadDate": file.upload_date.strftime("%d-%m-%Y")
                } for file in files
            ]
        }
        
        if transaction.transaction_type == "INCOME":
            total_income += float(transaction.amount)
            transactions_by_type["INCOME"].append(transaction_dict)
        else:
            total_expense += float(transaction.amount)
            transactions_by_type["EXPENSE"].append(transaction_dict)

    # Calculate carry forward
    previous_transactions = (
        db.query(Transaction)
        .filter(func.date(Transaction.date) < date.date())
        .all()
    )
    
    carry_forward = db.query(
    func.sum(
        case(
            (Transaction.transaction_type == "INCOME", Transaction.amount),
            else_=-Transaction.amount
        )
    )
    ).filter(func.date(Transaction.date) < date.date()).scalar() or 0

    return {
        "transactionsByType": transactions_by_type,
        "carryForward": carry_forward,
        "totalIncome": total_income,
        "totalExpense": total_expense,
        "balance": total_income - total_expense,
        "username": current_user
    }
    
@router.get("/summary/grouped", response_model=GroupedDashboardSummary)
async def get_grouped_summary(
    startDate: str,
    endDate: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    start_date = datetime.strptime(startDate, "%Y-%m-%d")
    end_date = datetime.strptime(endDate, "%Y-%m-%d")
    
    # Calculate initial carry forward
    initial_carry_forward = db.query(
        func.sum(
            case(
                (Transaction.transaction_type == "INCOME", Transaction.amount),
                else_=-Transaction.amount
            )
        )
    ).filter(func.date(Transaction.date) < start_date.date()).scalar() or 0
    
    # Get all transactions in date range
    transactions = (
        db.query(Transaction)
        .filter(
            func.date(Transaction.date).between(start_date.date(), end_date.date())
        )
        .order_by(Transaction.date.desc())
        .all()
    )
    
    # Group transactions by date
    transactions_by_date = {}
    for transaction in transactions:
        date_str = transaction.date.strftime("%d-%m-%Y")
        if date_str not in transactions_by_date:
            transactions_by_date[date_str] = {"income": [], "expense": []}
        
        transaction_dict = create_transaction_dict(transaction, db)
        if transaction.transaction_type == "INCOME":
            transactions_by_date[date_str]["income"].append(transaction_dict)
        else:
            transactions_by_date[date_str]["expense"].append(transaction_dict)
    
    # Calculate daily summaries
    daily_summaries = []
    running_balance = initial_carry_forward
    total_income = 0
    total_expense = 0
    
    for date_str, transactions in transactions_by_date.items():
        daily_income = sum(t["amount"] for t in transactions["income"])
        daily_expense = sum(t["amount"] for t in transactions["expense"])
        
        daily_summary = DailySummary(
            date=date_str,
            carryForward=running_balance,
            totalIncome=daily_income,
            totalExpense=daily_expense,
            incomeTransactions=transactions["income"],
            expenseTransactions=transactions["expense"],
            balance=running_balance + daily_income - daily_expense
        )
        
        running_balance = daily_summary.balance
        total_income += daily_income
        total_expense += daily_expense
        daily_summaries.append(daily_summary)
    
    return GroupedDashboardSummary(
        carryForward=initial_carry_forward,
        totalIncome=total_income,
        totalExpense=total_expense,
        balance=initial_carry_forward + total_income - total_expense,
        dailySummaries=daily_summaries
    )

def create_transaction_dict(transaction: Transaction, db: Session) -> dict:
    files = (
        db.query(File)
        .join(TransactionFile)
        .filter(TransactionFile.transaction_id == transaction.id)
        .all()
    )
    
    return {
        "id": transaction.id,
        "date": transaction.date.strftime("%d-%m-%Y"),
        "creationDate": transaction.creation_date.strftime("%d-%m-%Y %I:%M:%S %p"),
        "modificationDate": transaction.modification_date.strftime("%d-%m-%Y %I:%M:%S %p"),
        "title": transaction.title,
        "party": transaction.party,
        "amount": float(transaction.amount),
        "transactionType": transaction.transaction_type,
        "description": transaction.description,
        "fileInfos": [
            {
                "fileUuid": file.file_uuid,
                "filename": file.filename,
                "uploadDate": file.upload_date.strftime("%d-%m-%Y")
            } for file in files
        ]
    }