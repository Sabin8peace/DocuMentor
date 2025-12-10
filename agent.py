import os
import fitz  # PyMuPDF
import google.generativeai as genai
from pinecone import Pinecone
from db import get_resource_by_title
from dotenv import load_dotenv

load_dotenv()

# -------------------------------
# CONFIGURE GOOGLE GEMINI
# -------------------------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = "models/text-embedding-004"
LLM_MODEL = "models/gemini-2.5-flash"
# LLM_MODEL = "models/gemini-1.5-flash"

# -------------------------------
# CONFIGURE PINECONE
# -------------------------------
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pc = Pinecone(api_key=PINECONE_API_KEY)

# Make sure the index exists
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
# Embedding
# -------------------------------


def embed_text(text):
    res = genai.embed_content(
        model=EMBED_MODEL,
        content=text
    )
    return res["embedding"]

# -------------------------------
# Answer Query (RAG)
# -------------------------------


def answer_query(question, selected_title):
    """
    1️⃣ Fetch resource from DB
    2️⃣ Combine source_text + PDF text
    3️⃣ Embed combined text
    4️⃣ Upsert vector to Pinecone
    5️⃣ Embed question and query Pinecone
    6️⃣ Call LLM using retrieved context
    """
    # Fetch DB row
    row = get_resource_by_title(selected_title)
    if not row:
        return "Resource not found."

    resource_id, source_text, source_file, title, description = row

    # Extract PDF
    pdf_text = extract_pdf_text(source_file)

    # Combine DB + PDF text
    combined_text = (source_text or "") + "\n\n" + (pdf_text or "")

    # Embed combined text
    vector = embed_text(combined_text)

    # Upsert into Pinecone
    vector_index.upsert([
        (f"resource_{resource_id}", vector, {
         "title": title, "text": combined_text})
    ])

    # Embed user question
    question_vector = embed_text(question)

    # Query Pinecone with filter
    results = vector_index.query(
        vector=question_vector,
        top_k=3,
        include_metadata=True,
        filter={"title": title}
    )

    # Build context from top matches
    context = ""
    if results.matches:
        for match in results.matches:
            context += match.metadata["text"] + "\n\n"
    else:
        context = combined_text  # fallback

    # Final LLM prompt
    prompt = f"""
Use ONLY the following context to answer:

{context}

Question: {question}

If the answer is not in the context, say "I don't know based on the provided documents."
"""

    # Call LLM
    model = genai.GenerativeModel(LLM_MODEL)
    response = model.generate_content(prompt)

    return response.text
