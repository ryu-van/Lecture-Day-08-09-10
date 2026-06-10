#!/usr/bin/env python3
"""
Interactive command-line query tool for Day 10 ChromaDB knowledge base.
"""

import os
import sys
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

def main():
    db_path = os.environ.get("CHROMA_DB_PATH", "./chroma_db")
    if db_path.startswith("./") or db_path.startswith("../") or not os.path.isabs(db_path):
        from pathlib import Path
        db_path = str(Path(__file__).resolve().parent / db_path)
    collection_name = os.environ.get("CHROMA_COLLECTION", "day10_kb")
    model_name = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    print(f"--- Đang kết nối tới ChromaDB tại: {db_path} ---")
    client = chromadb.PersistentClient(path=db_path)
    emb = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
    
    try:
        col = client.get_collection(name=collection_name, embedding_function=emb)
        print(f"Đã tải thành công collection: {collection_name} (Hiện có {col.count()} chunks)")
    except Exception as e:
        print(f"Lỗi: Không tìm thấy collection '{collection_name}'. Hãy chạy 'python etl_pipeline.py run' trước!")
        return 1

    print("\nHệ thống sẵn sàng! Nhập câu hỏi của bạn (Gõ 'exit' hoặc 'quit' để thoát).\n")
    while True:
        try:
            query = input("Hỏi: ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break
            
            res = col.query(query_texts=[query], n_results=3)
            docs = res.get("documents", [[]])[0]
            metas = res.get("metadatas", [[]])[0]
            distances = res.get("distances", [[]])[0]

            print(f"\n--- Kết quả tìm kiếm (Top 3) ---")
            for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), 1):
                print(f"{i}. [Doc ID: {meta.get('doc_id')}] (Effective: {meta.get('effective_date')}) | Khoảng cách: {dist:.4f}")
                print(f"   Nội dung: {doc}")
                print("-" * 50)
            print()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Lỗi khi truy vấn: {e}\n")

if __name__ == "__main__":
    sys.exit(main())
