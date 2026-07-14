import os
from dotenv import load_dotenv
load_dotenv()

# Hyperparameters
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
RETRIEVER_K = 3

# Models
MODEL_EMBEDDING = "gemini-embedding-2-preview"
LLM_MODEL = "gemini-2.5-flash"
LLM_MAX_TOKENS = 500
LLM_TEMPERATURE = 0.3

# Paths
CHROMA_DIR = "data/chroma"

# Prompt templates
SYSTEM_PROMPT = """
      You are a helpful AI assistant for question-answering tasks.
      Answers should have this structure:

      1. 3 Lines summary of the answer
      2. Provide the reference code for the question asked,

      For example,
      {
            Input : What is the boilerplate of java?
            Response : The boilerplate of Java refers to the standard code structure and syntax that is commonly used in Java programming. It includes elements such as class definitions, method declarations, and import statements that are necessary for a Java program to function correctly. 
            Here is the reference code for the boilerplate of Java:
            package example;
            public class Main {
            public static void main(String[] args) {
                  System.out.println("Hello, World!");
            }
            }
      }
      Use the retrieved context below to answer the user's question.
      If the answer cannot be found in the provided context, respond with: "I don't know."

      Do not make up information.
      Keep your response concise and no longer than three sentences.

    Context: {context}
"""