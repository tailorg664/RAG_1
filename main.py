import sys
from src.ingestion import ingest_structured_pdf
from src.rag_chain import get_rag_chain

def run_query(query:str):
        chain = get_rag_chain()
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
    run_query("What is the syntax for creating binary search in java?")