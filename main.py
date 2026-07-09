import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
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
vector_store = Chroma.from_documents(docs,embedding=embeddings,persist_directory="data/chroma")

retriever = vector_store.as_retriever(search_type="similarity",search_kwargs={"k":3})

retrieved_docs = retriever.invoke("Who is sappho?")

# LLM integration
llm = ChatGoogleGenerativeAI(
      model = "gemini-2.5-flash",
      temperature = 0.3,
      max_tokens  = 500
)

# system prompt

system_prompt = """
    You are a helpful AI assistant for question-answering tasks.

Use the retrieved context below to answer the user's question.
If the answer cannot be found in the provided context, respond with: "I don't know."

Do not make up information.
Keep your response concise and no longer than three sentences.

    Context: {context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

document_chain = create_stuff_documents_chain(
    llm=llm,
    prompt=prompt,
)

rag_chain = create_retrieval_chain(
    retriever=retriever,
    combine_docs_chain=document_chain,
)

query = "Who is sappho?"
print(f"Sending query to Gemini : {query}")


# giving "input" as the key because we defined it in the prompt template


result = rag_chain.invoke({"input": query})

#  Print the final curated result
print("\n================== GEMINI ANSWER ==================")
print(result["answer"])
print("===================================================")

