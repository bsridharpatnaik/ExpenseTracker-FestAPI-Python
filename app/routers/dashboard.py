from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, File, TransactionFile
from app.auth import get_current_user
from datetime import datetime
from sqlalchemy import func
from typing import Dict, List
from app.schemas import DashboardSummary

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
    
    carry_forward = sum(
        float(t.amount) if t.transaction_type == "INCOME" else -float(t.amount)
        for t in previous_transactions
    )

    return {
        "transactionsByType": transactions_by_type,
        "carryForward": carry_forward,
        "totalIncome": total_income,
        "totalExpense": total_expense,
        "balance": total_income - total_expense,
        "username": current_user
    }