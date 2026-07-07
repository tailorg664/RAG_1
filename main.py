import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma 
from dotenv import load_dotenv
load_dotenv()

loader = PyPDFLoader("data/hso.pdf")
data = loader.load()
print("__Loading document from data/hso.pdf__")
print("length is", len(data))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)

docs = text_splitter.split_documents(data)
print("length after splitting is", len(docs))

embeddings = GoogleGenerativeAIEmbeddings(
      model = "gemini-embedding-2-preview"
)
vector = 