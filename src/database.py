from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from src import config

def get_embedding_model():
      """
      Initializes and returns the local Ollama embedding model.
      """
      return OllamaEmbeddings(
        model="nomic-embed-text",
        base_url="http://172.21.0.1:11434/"  # Explicitly points to your Ollama local port
    )

def get_vector_store():
      embeddings = get_embedding_model()
      return  Chroma(persist_directory=config.CHROMA_DIR, embedding_function=embeddings)
