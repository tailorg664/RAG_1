from google import genai
from dotenv import load_dotenv
load_dotenv()

client = genai.Client()

KNOWLEDGE_BASE = {
    "shipping":"Our company offers free shipping on orders over $26. Standard shipping takes 5-7 business days, while expedited shipping takes 4-7 business days.",
    "returns":"We accept returns within 16 days of purchase. Items must be in their original condition and packaging. Please contact our customer service for return instructions.",
    "support":"Our customer support team is available 24/7 to assist you with any questions or concerns. You can reach us via email, phone, or live chat on our website : https://www.example.com/support.",
}

# 2. The User's Question
user_question = "How long does it take for my package to arrive?"

context = ""
if "shipping" in user_question.lower() or "package" in user_question.lower():
    context = KNOWLEDGE_BASE["shipping"]
if "shipping" in user_question or "package" in user_question or "arrive" in user_question:
    context = KNOWLEDGE_BASE["shipping"]
elif "return" in user_question or "refund" in user_question:
    context = KNOWLEDGE_BASE["returns"]
elif "help" in user_question or "support" in user_question:
    context = KNOWLEDGE_BASE["support"]
else:
    context = "No specific company policy found for this question."

engineering_prompt = f"""
You are a helpful assistant that provides information based on the company's policies.

Background Facts: {context}
User's Question: {user_question}

Please provide a clear and concise answer to the user's question based on the provided context.
"""
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=engineering_prompt,
)

print("___AI Response___")
print(response.text)