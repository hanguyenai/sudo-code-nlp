import os
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from .config import config
import google.generativeai as genai


class RAGPipeline:
    def __init__(self):
        """Initialize RAG Pipeline với Gemini và ChromaDB"""
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.qa_chain = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Khởi tạo các component của RAG"""
        # Configure Gemini API
        if config.GOOGLE_API_KEY:
            genai.configure(api_key=config.GOOGLE_API_KEY)
        
        # Initialize embeddings
        print("Initializing embeddings model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize Gemini LLM
        print("Initializing Gemini LLM...")
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Load or create vector store
        if os.path.exists(config.CHROMA_PERSIST_DIR):
            print("Loading existing vector store...")
            self.vectorstore = Chroma(
                persist_directory=config.CHROMA_PERSIST_DIR,
                embedding_function=self.embeddings
            )
        else:
            print("Vector store will be created when documents are indexed.")
    
    def load_and_process_pdfs(self, pdf_dir: str) -> List[Any]:
        """Load và xử lý các file PDF"""
        documents = []
        
        if not os.path.exists(pdf_dir):
            print(f"PDF directory {pdf_dir} không tồn tại!")
            return documents
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"Không tìm thấy file PDF trong {pdf_dir}")
            return documents
        
        print(f"Đang load {len(pdf_files)} file PDF...")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                documents.extend(docs)
                print(f"✓ Loaded: {pdf_file} ({len(docs)} pages)")
            except Exception as e:
                print(f"✗ Error loading {pdf_file}: {str(e)}")
        
        return documents
    
    def create_chunks(self, documents: List[Any]) -> List[Any]:
        """Chia documents thành chunks nhỏ hơn"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
    
    def create_vector_store(self, chunks: List[Any]):
        """Tạo vector store từ chunks"""
        print("Creating vector store...")
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR
        )
        self.vectorstore.persist()
        print(f"Vector store created and persisted to {config.CHROMA_PERSIST_DIR}")
    
    def setup_qa_chain(self):
        """Thiết lập QA chain với custom prompt"""
        if self.vectorstore is None:
            raise ValueError("Vector store chưa được khởi tạo. Hãy index documents trước!")
        
        # Custom prompt template
        prompt_template = """Bạn là một AI assistant chuyên về Machine Learning và Deep Learning. 
Sử dụng các thông tin từ tài liệu được cung cấp để trả lời câu hỏi một cách chính xác và chi tiết.

Context từ tài liệu:
{context}

Câu hỏi: {question}

Hướng dẫn trả lời:
- Trả lời bằng tiếng Việt (trừ khi được yêu cầu khác)
- Dựa trên thông tin từ context được cung cấp
- Nếu không tìm thấy thông tin trong context, hãy nói rõ
- Trích dẫn các phần liên quan từ tài liệu khi có thể
- Giải thích các khái niệm kỹ thuật một cách dễ hiểu

Trả lời:"""

        PROMPT = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        # Create retriever
        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": config.TOP_K_RESULTS}
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": PROMPT}
        )
        
        print("QA chain setup completed!")
    
    def query(self, question: str) -> Dict[str, Any]:
        """Truy vấn câu hỏi và nhận câu trả lời"""
        if self.qa_chain is None:
            self.setup_qa_chain()
        
        try:
            result = self.qa_chain({"query": question})
            
            # Format response
            response = {
                "answer": result["result"],
                "sources": []
            }
            
            # Add source documents
            for doc in result.get("source_documents", []):
                source_info = {
                    "content": doc.page_content[:200] + "...",  # Preview
                    "metadata": doc.metadata
                }
                response["sources"].append(source_info)
            
            return response
            
        except Exception as e:
            return {
                "answer": f"Lỗi khi xử lý câu hỏi: {str(e)}",
                "sources": [],
                "error": str(e)
            }
    
    def index_documents(self, pdf_dir: str = None):
        """Index tất cả documents từ thư mục PDF"""
        if pdf_dir is None:
            pdf_dir = config.PDF_DIR
        
        # Load PDFs
        documents = self.load_and_process_pdfs(pdf_dir)
        
        if not documents:
            print("Không có documents để index!")
            return False
        
        # Create chunks
        chunks = self.create_chunks(documents)
        
        # Create vector store
        self.create_vector_store(chunks)
        
        # Setup QA chain
        self.setup_qa_chain()
        
        print("✓ Indexing completed successfully!")
        return True


# Singleton instance
_rag_pipeline = None

def get_rag_pipeline() -> RAGPipeline:
    """Get singleton instance của RAG pipeline"""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline