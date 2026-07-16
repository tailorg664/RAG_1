import sys
from src.ingestion import ingest_structured_pdf
from src.rag_chain import get_rag_chain
from src.query_rag import ask_dsa_system_guided

def run_query(query:str):
        chain = ask_dsa_system_guided(query)
        print(f"Sending query to Gemini: {query}")

        response = chain.invoke({"input": query})
        print("\n================== GEMINI ANSWER ==================")
        print(response["answer"])
        print("===================================================")
        return response

if __name__ == "__main__":
    # Quick check if you want to ingest or query
    # if len(sys.argv) > 1 and sys.argv[1] == "--ingest":
    #     ingest_document("data/dsa.pdf")
    # else:
    run_query("What is java?")