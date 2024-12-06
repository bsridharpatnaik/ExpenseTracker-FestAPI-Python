from fastapi import FastAPI, Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from app import models, database
from app.database import SessionLocal
from app.auth import get_current_user
import uuid
from datetime import datetime
from pydantic import BaseModel
from app.auth import verify_password, get_current_user, create_access_token
from fastapi.responses import Response

models.Base.metadata.create_all(bind=database.engine, checkfirst=True)
app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/auth/login")
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/file/upload")
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
    
@app.get("/api/file/download/{file_uuid}")
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