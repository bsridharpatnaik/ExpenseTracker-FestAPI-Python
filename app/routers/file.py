from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import File
from app.auth import get_current_user
from fastapi.responses import Response
import uuid
from datetime import datetime
from app import models

router = APIRouter(prefix="/api/file")

@router.post("/upload")
async def upload_file(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    file_content = await file.read()
    file_uuid = str(uuid.uuid4())
    
    db_file = models.File(
        file_uuid=file_uuid,
        filename=file.filename,
        file_data=file_content,
        upload_date=datetime.utcnow()
    )
    
    db.add(db_file)
    db.commit()
    
    return {
        "fileUuid": file_uuid,
        "filename": file.filename,
        "uploadDate": db_file.upload_date.strftime("%d-%m-%Y")
    }
    
@router.get("/download/{file_uuid}")
async def download_file(
    file_uuid: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    file = db.query(models.File).filter(models.File.file_uuid == file_uuid).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
        
    from fastapi.responses import Response
    return Response(
        content=file.file_data,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={file.filename}"
        }
    )