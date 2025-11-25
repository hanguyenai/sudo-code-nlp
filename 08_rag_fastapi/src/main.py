from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
from starlette.requests import Request

from src.rag_pipeline import get_rag_pipeline
from src.config import config

# Initialize FastAPI app
app = FastAPI(
    title="RAG Pipeline với Gemini API",
    description="Hệ thống trả lời câu hỏi từ tài liệu PDF sử dụng RAG và Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files và templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models
class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    error: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: str
    documents_indexed: bool
    vector_store_exists: bool


# Initialize RAG pipeline
rag_pipeline = get_rag_pipeline()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Trang chủ với giao diện web"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    """Kiểm tra trạng thái của hệ thống"""
    vector_store_exists = os.path.exists(config.CHROMA_PERSIST_DIR)
    documents_indexed = rag_pipeline.vectorstore is not None
    
    return StatusResponse(
        status="ready" if documents_indexed else "not_ready",
        message="Hệ thống đã sẵn sàng" if documents_indexed else "Cần index documents",
        documents_indexed=documents_indexed,
        vector_store_exists=vector_store_exists
    )


@app.post("/api/index")
async def index_documents():
    """Index tất cả documents trong thư mục PDF"""
    try:
        # Ensure PDF directory exists
        os.makedirs(config.PDF_DIR, exist_ok=True)
        
        # Check if there are PDFs
        pdf_files = [f for f in os.listdir(config.PDF_DIR) if f.endswith('.pdf')]
        
        if not pdf_files:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": f"Không tìm thấy file PDF trong {config.PDF_DIR}. Hãy upload PDF trước!"
                }
            )
        
        # Index documents
        success = rag_pipeline.index_documents()
        
        if success:
            return {
                "status": "success",
                "message": f"Đã index thành công {len(pdf_files)} file PDF",
                "files": pdf_files
            }
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Lỗi khi index documents"
                }
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Lỗi: {str(e)}"
            }
        )


@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload file PDF"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Chỉ chấp nhận file PDF")
        
        # Ensure directory exists
        os.makedirs(config.PDF_DIR, exist_ok=True)
        
        # Save file
        file_path = os.path.join(config.PDF_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success",
            "message": f"Upload thành công: {file.filename}",
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi upload: {str(e)}")


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Truy vấn câu hỏi từ documents"""
    try:
        # Check if system is ready
        if rag_pipeline.vectorstore is None:
            raise HTTPException(
                status_code=400,
                detail="Hệ thống chưa sẵn sàng. Hãy index documents trước!"
            )
        
        # Query
        result = rag_pipeline.query(request.question)
        
        return QueryResponse(
            answer=result.get("answer", ""),
            sources=result.get("sources", []),
            error=result.get("error")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return QueryResponse(
            answer="",
            sources=[],
            error=str(e)
        )


@app.get("/api/documents")
async def list_documents():
    """Liệt kê các documents đã upload"""
    try:
        if not os.path.exists(config.PDF_DIR):
            return {"documents": []}
        
        pdf_files = [f for f in os.listdir(config.PDF_DIR) if f.endswith('.pdf')]
        
        documents = []
        for filename in pdf_files:
            file_path = os.path.join(config.PDF_DIR, filename)
            file_size = os.path.getsize(file_path)
            documents.append({
                "filename": filename,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2)
            })
        
        return {"documents": documents}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Xóa một document"""
    try:
        file_path = os.path.join(config.PDF_DIR, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File không tồn tại")
        
        os.remove(file_path)
        
        return {
            "status": "success",
            "message": f"Đã xóa {filename}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )