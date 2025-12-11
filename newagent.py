import os
import fitz  # PyMuPDF
from google import genai
from pinecone import Pinecone
from db import get_resource_by_title
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# CONFIGURE GOOGLE GEMINI (NEW API)
# -------------------------------
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "models/text-embedding-004"
# LLM_MODEL = "models/gemini-3-pro-preview"   # or "gemini-3-pro-preview"
LLM_MODEL = "models/gemini-2.5-flash"   # or "gemini-3-pro-preview"

# -------------------------------
# CONFIGURE PINECONE
# -------------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

if "student-kb" not in pc.list_indexes().names():
    pc.create_index(name="student-kb", dimension=768)

vector_index = pc.Index("student-kb")


# -------------------------------
# PDF Extraction
# -------------------------------
def extract_pdf_text(file_path):
    if not file_path or not os.path.exists(file_path):
        return ""
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# -------------------------------
# Embedding (NEW GEMINI WAY)
# -------------------------------
def embed_text(text):
    res = client.models.embed_content(
        model=EMBED_MODEL,
        contents=text
    )
    return res.embeddings[0].values   # New API structure


# -------------------------------
# Answer Query (RAG)
# -------------------------------
def answer_query(question, selected_title):

    row = get_resource_by_title(selected_title)
    if not row:
        return "Resource not found."

    resource_id, source_text, source_file, title, description = row

    pdf_text = extract_pdf_text(source_file)
    combined_text = (source_text or "") + "\n\n" + (pdf_text or "")

    vector = embed_text(combined_text)

    # Upsert into Pinecone
    vector_index.upsert([
        (f"resource_{resource_id}", vector, {
         "title": title, "text": combined_text})
    ])

    # Embed question
    question_vector = embed_text(question)

    # Query Pinecone
    results = vector_index.query(
        vector=question_vector,
        top_k=3,
        include_metadata=True,
        filter={"title": title}
    )

    # Build context
    context = ""
    if results.matches:
        for match in results.matches:
            context += match.metadata["text"] + "\n\n"
    else:
        context = combined_text

    # Final prompt
    prompt = f"""
Use ONLY the following context to answer:

{context}

Question: {question}

If the answer is not in the context, say:
"I don't know based on the provided documents."
"""

    # Call LLM (NEW GEMINI FORMAT)
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt
    )

    return response.text
