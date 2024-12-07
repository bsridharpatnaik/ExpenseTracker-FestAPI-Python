from app import models
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction, TransactionFile, File
from app.schemas import TransactionRequest, TransactionResponse, TransactionType
from app.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/transaction")

@router.post("", response_model=TransactionResponse)
async def create_transaction(
    transaction_data: TransactionRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    files = []
    for file_request in transaction_data.files:
        file = db.query(File).filter(File.file_uuid == file_request.fileUuid).first()
        if not file:
            raise HTTPException(status_code=404, detail=f"File not found: {file_request.fileUuid}")
        files.append(file)
    
    transaction = Transaction(
        transaction_type=transaction_data.transactionType,
        date=datetime.strptime(transaction_data.date, "%d-%m-%Y"),
        title=transaction_data.title,
        party=transaction_data.party,
        amount=transaction_data.amount,
        description=transaction_data.description
    )
    db.add(transaction)
    db.flush()

    for file in files:
        transaction_file = TransactionFile(
            transaction_id=transaction.id,
            file_id=file.id
        )
        db.add(transaction_file)
    
    db.commit()
    
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
    