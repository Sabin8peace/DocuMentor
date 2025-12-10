# RAG Chatbot with Resource Manager

A **Retrieval-Augmented Generation (RAG) Chatbot** powered by your database, allowing you to manage resources (PDFs and text) and answer questions intelligently using AI embeddings and LLMs. Built with **Streamlit**, **PostgreSQL**, **Pinecone**, and **Google Gemini / Groq**.

---

## 🔹 Features

### 1. Resource Management (CRUD)
- Add, edit, delete, and view resources.
- Each resource includes:
  - `Title`
  - `Description`
  - `Source Text`
  - `PDF File`
- PostgreSQL used for storage.

### 2. RAG Chatbot
- Select a resource from the database.
- Ask questions based on selected resource.
- Answers are generated using **RAG + LLM**, combining:
  - Text stored in DB (`source_text`)
  - PDF content (`source_file`)
- Similar documents are retrieved using **Pinecone** vector search.

### 3. Vector Embeddings
- Converts text and PDFs into vector embeddings.
- Stores vectors in Pinecone for fast similarity search.
- Queries use embeddings to fetch relevant context before generating answers.

### 4. Streamlit UI
- Intuitive interface for managing resources and asking questions.
- Dynamic spinner/progress bar while processing queries.
- Clean display of answers.

---

## 🔹 Tech Stack
- **Backend:** Python, PostgreSQL
- **Frontend:** Streamlit
- **Vector Search:** Pinecone
- **LLM / AI:** Google Gemini / Groq
- **PDF Parsing:** PyMuPDF (fitz)
- **Environment Management:** python-dotenv

---

## 🔹 Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <project-folder>
