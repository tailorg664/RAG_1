from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from src import config, database
from src.document_utils import split_pdf_by_toc
import sys
import os
import time
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def ingest_structured_pdf(file_path:str,pdf_offset:int = 0):
      print(f"\n[1/3] Slicing PDF into semantic topics using TOC mapping...")
      parent_docs = split_pdf_by_toc(file_path, offset=pdf_offset)
      child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE, 
        chunk_overlap=config.CHUNK_OVERLAP
      )
      all_child_chunks = []
      print("\n[2/3] Generating sub-chunks while maintaining chapter metadata...")
      
      for parent_doc in tqdm(parent_docs, desc="Processing Chapters"):
            chunks = child_splitter.split_documents([parent_doc])
            
            for chunk in chunks:
                  chunk.metadata.update({
                  "parent_section": parent_doc.metadata["section_id"],
                  "parent_title": parent_doc.metadata["title"],
                  "start_page": parent_doc.metadata["start_page"]
                  })
                  all_child_chunks.append(chunk)
      print(f"-> Generated {len(all_child_chunks)} small child chunks.")
      embeddings = database.get_embedding_model()
      vector_store = Chroma(
            persist_directory=config.CHROMA_DIR,
            embedding_function=embeddings
      )
      print("\n[3/3] Uploading chunks to Chroma (Strict Free-Tier Protocol)...")
    
      # Precision limits for your account
      BATCH_SIZE = 1
      DELAY_SECONDS = 13  # Keeps us under 5 RPM
      DAILY_LIMIT = 20    # Keeps us under 20 RPD
      
      # We only take the first 20 chunks to prevent daily quota crashes
      chunks_to_upload = all_child_chunks[:DAILY_LIMIT]
      total_chunks = len(chunks_to_upload)
      
      print(f"⚠️ Strict daily limit active! Uploading only the first {total_chunks} chunks today.")

      for i in tqdm(range(0, total_chunks, BATCH_SIZE), desc="Uploading to Vector DB"):
            batch = chunks_to_upload[i : i + BATCH_SIZE]
            vector_store.add_documents(documents=batch)
            
            # Only sleep if there are more chunks remaining in our 20-chunk limit
            if i + BATCH_SIZE < total_chunks:
                  time.sleep(DELAY_SECONDS)

      print(f"\n🎉 Successfully uploaded {total_chunks} chunks!")
      if len(all_child_chunks) > DAILY_LIMIT:
            print(f"💡 You have {len(all_child_chunks) - DAILY_LIMIT} chunks remaining. Run this again tomorrow to process the next batch.")

if __name__ == "__main__":
      ingest_structured_pdf("data/dsa.pdf",18)

      