from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from src import config, database

def get_rag_chain():
      # Load existing database and convert to retriever
      vector_store = database.get_vector_store()
      retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": config.RETRIEVER_K}
      )

      # Initialize the LLM with the Google Generative AI model

      llm = ChatGoogleGenerativeAI(
            model=config.LLM_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_output_tokens=config.LLM_MAX_TOKENS,
      )

      # Build the prompt template for the RAG chain
      prompt_template = ChatPromptTemplate.from_messages(
            [
                  ("system", config.SYSTEM_PROMPT),
                  ("human", "{input}"),
            ]
      )

      # Create the document chain using the LLM and prompt template
      
      document_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt_template,
      )
      return create_retrieval_chain(retriever=retriever, combine_docs_chain=document_chain)