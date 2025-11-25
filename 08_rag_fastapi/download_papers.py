#!/usr/bin/env python3
"""
Script để tải các AI papers phổ biến cho RAG pipeline
"""

import os
import requests
from pathlib import Path

# Thư mục lưu PDFs
PDF_DIR = Path("data/pdfs")
PDF_DIR.mkdir(parents=True, exist_ok=True)

# Danh sách các papers
PAPERS = [
    {
        "name": "Attention Is All You Need (Transformer)",
        "url": "https://arxiv.org/pdf/1706.03762.pdf",
        "filename": "attention_is_all_you_need.pdf"
    },
    {
        "name": "BERT: Pre-training of Deep Bidirectional Transformers",
        "url": "https://arxiv.org/pdf/1810.04805.pdf",
        "filename": "bert_paper.pdf"
    },
    {
        "name": "GPT-3: Language Models are Few-Shot Learners",
        "url": "https://arxiv.org/pdf/2005.14165.pdf",
        "filename": "gpt3_paper.pdf"
    },
    {
        "name": "ResNet: Deep Residual Learning for Image Recognition",
        "url": "https://arxiv.org/pdf/1512.03385.pdf",
        "filename": "resnet_paper.pdf"
    },
    {
        "name": "Vision Transformer (ViT)",
        "url": "https://arxiv.org/pdf/2010.11929.pdf",
        "filename": "vision_transformer.pdf"
    },
    {
        "name": "CLIP: Learning Transferable Visual Models",
        "url": "https://arxiv.org/pdf/2103.00020.pdf",
        "filename": "clip_paper.pdf"
    },
    {
        "name": "Stable Diffusion: High-Resolution Image Synthesis",
        "url": "https://arxiv.org/pdf/2112.10752.pdf",
        "filename": "stable_diffusion.pdf"
    },
    {
        "name": "LLaMA: Open and Efficient Foundation Language Models",
        "url": "https://arxiv.org/pdf/2302.13971.pdf",
        "filename": "llama_paper.pdf"
    }
]


def download_paper(paper_info):
    """Download một paper từ URL"""
    url = paper_info["url"]
    filename = paper_info["filename"]
    name = paper_info["name"]
    filepath = PDF_DIR / filename
    
    # Kiểm tra nếu đã tồn tại
    if filepath.exists():
        print(f"✓ {name} - Đã tồn tại, bỏ qua")
        return True
    
    print(f"⬇️  Đang tải: {name}...")
    
    try:
        # Download với stream để xử lý files lớn
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Lưu file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"✓ {name} - Hoàn thành ({file_size_mb:.2f} MB)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ {name} - Lỗi: {str(e)}")
        # Xóa file nếu download không hoàn chỉnh
        if filepath.exists():
            filepath.unlink()
        return False
    except Exception as e:
        print(f"✗ {name} - Lỗi không xác định: {str(e)}")
        if filepath.exists():
            filepath.unlink()
        return False


def main():
    """Main function"""
    print("=" * 70)
    print("📚 DOWNLOAD AI RESEARCH PAPERS")
    print("=" * 70)
    print()
    
    print(f"Thư mục lưu trữ: {PDF_DIR.absolute()}")
    print(f"Số lượng papers: {len(PAPERS)}")
    print()
    
    # Hỏi user muốn download papers nào
    print("Chọn papers muốn download:")
    print("0. Tất cả papers")
    for idx, paper in enumerate(PAPERS, 1):
        print(f"{idx}. {paper['name']}")
    print()
    
    choice = input("Nhập lựa chọn (0 hoặc số paper, cách nhau bởi dấu phẩy): ").strip()
    
    # Parse choices
    if choice == "0":
        selected_papers = PAPERS
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(",")]
            selected_papers = [PAPERS[i-1] for i in indices if 1 <= i <= len(PAPERS)]
        except (ValueError, IndexError):
            print("❌ Lựa chọn không hợp lệ!")
            return
    
    if not selected_papers:
        print("❌ Không có paper nào được chọn!")
        return
    
    print()
    print(f"Sẽ download {len(selected_papers)} paper(s)...")
    print()
    
    # Download papers
    success_count = 0
    for paper in selected_papers:
        if download_paper(paper):
            success_count += 1
        print()
    
    # Summary
    print("=" * 70)
    print(f"✓ Hoàn thành: {success_count}/{len(selected_papers)} papers")
    print(f"📁 Vị trí: {PDF_DIR.absolute()}")
    print()
    print("Bước tiếp theo:")
    print("1. Khởi động server: cd src && python main.py")
    print("2. Truy cập: http://localhost:8000")
    print("3. Nhấn 'Index Documents' để xử lý papers")
    print("4. Bắt đầu đặt câu hỏi!")
    print("=" * 70)


if __name__ == "__main__":
    main()