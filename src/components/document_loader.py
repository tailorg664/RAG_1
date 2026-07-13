import os
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/dsa.pdf")

data = loader.load()
