from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)

def chunk_documents(documents):
    return text_splitter.split_documents(documents)