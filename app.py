from newagent import answer_query  # import your RAG function
import streamlit as st
import os
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Local imports
from db import (
    get_all_resources,
    get_resource_by_title,
    create_resource,
    update_resource,
    delete_resource,
)

load_dotenv()


# ------------------------
# Helper: Extract PDF Text
# ------------------------
def extract_pdf_text(pdf_path):
    if not pdf_path:
        return ""

    try:
        full_path = os.path.join("documents", os.path.basename(pdf_path))
        text = ""
        with fitz.open(full_path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except:
        return ""


# ------------------------
# Sidebar Navigation
# ------------------------
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio(
    "Go to:", ["Manage Resources", "Ask Question Chatbot AI"]
)


# ============================================================
#                  PAGE 1 → CRUD INTERFACE
# ============================================================
if page == "Manage Resources":
    st.title("📁 Resource Manager")
    st.markdown(
        "Manage your knowledge base: upload PDFs or paste text to create, edit, or delete resources."
    )
    st.divider()

    crud_option = st.selectbox("Select Operation:", [
                               "Add", "Edit", "Delete", "View"])

    # ---------------------------------------------------------
    # ADD RESOURCE
    # ---------------------------------------------------------
    if crud_option == "Add":
        st.subheader("➕ Add New Resource")
        title = st.text_input("📝 Title")
        description = st.text_area("📝 Description")
        source_text = st.text_area("📝 Source Text")
        pdf_file = st.file_uploader("📄 Upload PDF (optional)", type=["pdf"])

        if st.button("💾 Save Resource"):
            if pdf_file:
                pdf_path = f"documents/{pdf_file.name}"
                with open(pdf_path, "wb") as f:
                    f.write(pdf_file.read())
            else:
                pdf_path = None

            create_resource(source_text, pdf_path, title, description)
            st.success("✅ Resource Added Successfully!")

    # ---------------------------------------------------------
    # EDIT RESOURCE
    # ---------------------------------------------------------
    if crud_option == "Edit":
        st.subheader("✏️ Edit Resource")
        all_resources = get_all_resources()
        titles = [r[0] for r in all_resources]

        selected_title = st.selectbox("📚 Select Resource", titles)
        record = get_resource_by_title(selected_title)
        id, source_text, source_file, title, description = record

        new_title = st.text_input("📝 Title", title)
        new_description = st.text_area("📝 Description", description)
        new_source_text = st.text_area("📝 Source Text", source_text)
        new_pdf = st.file_uploader("📄 Change PDF (optional)", type=["pdf"])

        if st.button("💾 Update Resource"):
            pdf_path = source_file
            if new_pdf:
                pdf_path = f"documents/{new_pdf.name}"
                with open(pdf_path, "wb") as f:
                    f.write(new_pdf.read())

            update_resource(id, new_source_text, new_title,
                            new_description, pdf_path)
            st.success("✅ Resource Updated Successfully!")

    # ---------------------------------------------------------
    # DELETE RESOURCE
    # ---------------------------------------------------------
    if crud_option == "Delete":
        st.subheader("🗑 Delete Resource")
        all_resources = get_all_resources()
        titles = [r[0] for r in all_resources]
        selected_title = st.selectbox("📚 Select Resource", titles)
        record = get_resource_by_title(selected_title)
        id, source_text, source_file, title, description = record

        if st.button("🗑 Delete"):
            delete_resource(id)
            st.success("✅ Resource Deleted Successfully!")

    # ---------------------------------------------------------
    # VIEW RESOURCES
    # ---------------------------------------------------------
    if crud_option == "View":
        st.subheader("📄 All Resources")
        all_resources = get_all_resources()
        for t, d in all_resources:
            st.markdown(f"### 📌 {t}")
            st.info(d)
            st.divider()


# ============================================================
#          PAGE 2 → RAG CHATBOT WITH DB SELECTION
# ============================================================
if page == "Ask Question Chatbot AI":
    st.title("📚 Knowledge Base AI Chatbot")

    # Load resources
    resources = get_all_resources()  # [(title, description)]
    titles = [r[0] for r in resources]

    selected_title = st.selectbox("Select Resource", titles)
    description = next((d for t, d in resources if t == selected_title), "")
    st.info(description)

    # User input
    user_query = st.text_input("Ask a question:")
    if st.button("Ask") and user_query:

        # Spinner while processing
        with st.spinner("🤖 Generating answer, please wait..."):
            try:
                answer = answer_query(user_query, selected_title)
                st.subheader("💬 Answer:")
                st.write(answer)
            except Exception as e:
                err_msg = str(e)
                if "Quota exceeded" in err_msg or "429" in err_msg:
                    # Try to parse retry time from the error
                    import re
                    match = re.search(
                        r"retry_delay.*?seconds: ([\d\.]+)", err_msg)
                    retry_seconds = float(match.group(1)) if match else None

                    if retry_seconds:
                        from datetime import datetime, timedelta
                        retry_time = datetime.now() + timedelta(seconds=retry_seconds)
                        retry_str = retry_time.strftime("%H:%M:%S")
                        st.error(
                            f"⚠️ API quota exceeded! You have reached the daily limit for Gemini API.\n"
                            f"⏱ You can try again after approximately {int(retry_seconds)} seconds "
                            f"(around {retry_str}).\n"
                            f"More info: https://ai.google.dev/gemini-api/docs/rate-limits"
                        )
                    else:
                        st.error(
                            "⚠️ API quota exceeded! Please wait and try again later.\n"
                            "More info: https://ai.google.dev/gemini-api/docs/rate-limits"
                        )
                else:
                    st.error(f"❌ An error occurred: {err_msg}")

# if page == "Ask Question Chatbot AI":
#     st.title("🤖 Ask Your Knowledge AI")
#     st.markdown(
#         "Select a resource and ask any question. The AI will provide answers based on your database documents."
#     )
#     st.divider()

#     # Load resources
#     resources = get_all_resources()  # [(title, description)]
#     titles = [r[0] for r in resources]

#     selected_title = st.selectbox("📚 Select Resource", titles)
#     description = next((d for t, d in resources if t == selected_title), "")
#     if description:
#         st.markdown("**📝 Description:**")
#         st.info(description)

#     # User input
#     user_query = st.text_input("💬 Ask your question here:")
#     if st.button("🚀 Get Answer") and user_query:

#         # Spinner while processing
#         with st.spinner("🤖 AI is thinking... fetching the best answer for you..."):
#             answer = answer_query(user_query, selected_title)

#         # Show answer after processing
#         st.success("✅ Answer generated!")
#         st.subheader("💡 Answer:")
#         st.write(answer)
