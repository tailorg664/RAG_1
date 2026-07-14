from langchain_community.documents_loaders import PDFLoader

loader = PDFLoader("../data/dsa.pdf")

CHUNK_SIZE = 1000
MODEL_EMBEDDING = "gemini-embedding-2-preview"
LLM_MODEL = "gemini-2.5-flash"
MAX_TOKENS = 500
TEMPERATURE = 0.3
