from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src import config

def get_embedding_model():
      return GoogleGenerativeAIEmbeddings(model = config.MODEL_EMBEDDING)

def get_vector_store():
      embeddings = get_embedding_model()
      return  Chroma(persist_directory=config.CHROMA_DIR, embedding_function=embeddings)
