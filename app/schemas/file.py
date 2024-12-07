from pydantic import BaseModel

class FileResponse(BaseModel):
    fileUuid: str
    filename: str
    uploadDate: str