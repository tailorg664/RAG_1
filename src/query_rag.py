import sys
import os
from src import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from src.database import get_vector_store
from src.document_utils import TOC_MAP  # Importing our structural map reference!

def find_best_section_reference(query_text: str) -> str:
    """
    A lightweight router that scans our Table of Contents map keys 
    to find the most relevant structural reference.
    """
    query_lower = query_text.lower()
    best_section = None
    max_matches = 0

    # Simple keyword routing against our TOC Reference map
    for section_id, (page, title) in TOC_MAP.items():
        title_words = title.lower().replace(",", "").replace("-", " ").split()
        # Count how many words in the section title match the user query
        matches = sum(1 for word in title_words if word in query_lower and len(word) > 2)
        
        if matches > max_matches:
            max_matches = matches
            best_section = section_id
            
    return best_section

def ask_dsa_system_guided(query_text: str):
      vector_store = get_vector_store()

      # 1. Look up our "Reference Map" first
      target_section = find_best_section_reference(query_text)

      # 2. Configure the retriever with a strict metadata filter if a section was found
      if target_section:
            print(f"🎯 Reference Router matched query to Section {target_section} ({TOC_MAP[target_section][1]})")
            # This metadata filter forces Chroma to ignore the rest of the book completely!
            retriever = vector_store.as_retriever(
            search_kwargs={
                  "k": 3,
                  "filter": {"parent_section": target_section} 
            }
            )
      else:
            print("🌐 No direct reference matched. Performing a global database search...")
            retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            
      # 3. Rest of your LLM generation chain...
      llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
      )

      # [Insert standard RAG chain logic here...]
      prompt_template = ChatPromptTemplate.from_messages(
            [
                  ("system", config.SYSTEM_PROMPT),
                  ("human", "{input}"),
            ]
      )
      document_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt_template,
      )
      return create_retrieval_chain(retriever=retriever, combine_docs_chain=document_chain)