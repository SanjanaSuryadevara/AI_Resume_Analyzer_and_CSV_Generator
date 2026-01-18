import streamlit as st
import zipfile
import pandas as pd
from io import BytesIO
import os
import json

from google import genai
from dotenv import load_dotenv

import PyPDF2
from docx import Document

# -------------------------------------------------
# ENV SETUP
# -------------------------------------------------
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer (Gemini)",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI-Powered Resume Analyzer & CSV Generator")
st.caption("Upload a ZIP file containing resumes (PDF / DOCX)")

# -------------------------------------------------
# FILE TEXT EXTRACTION
# -------------------------------------------------
def extract_text(file_bytes, filename):
    text = ""

    if filename.lower().endswith(".pdf"):
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    elif filename.lower().endswith(".docx"):
        doc = Document(BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"

    if not text.strip():
        raise ValueError("No readable text found (image-based or scanned PDF)")

    return text.strip()

# -------------------------------------------------
# STRICT JSON PROMPT
# -------------------------------------------------
def build_prompt(resume_text):
    return f"""
You are an AI resume parser.

Return ONLY valid JSON.
NO markdown.
NO explanation.
NO extra text.

JSON FORMAT:
{{
  "name": "",
  "email": "",
  "phone": "",
  "skills": [],
  "education": "",
  "experience_summary": "",
  "linkedin": ""
}}

Resume Text:
{resume_text}
"""

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------
uploaded_zip = st.file_uploader(
    "Upload ZIP file containing resumes (PDF / DOCX)",
    type=["zip"]
)

# -------------------------------------------------
# PROCESS RESUMES
# -------------------------------------------------
if uploaded_zip and st.button("Analyze Resumes"):
    results = []

    with zipfile.ZipFile(uploaded_zip, "r") as z:
        resume_files = [f for f in z.namelist() if f.lower().endswith((".pdf", ".docx"))]

        if not resume_files:
            st.error("No PDF or DOCX files found inside ZIP.")
        else:
            for name in resume_files:
                try:
                    resume_text = extract_text(z.read(name), name)
                    prompt = build_prompt(resume_text)

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=prompt
                    )

                    raw = response.text.strip()
                    raw = raw.replace("```json", "").replace("```", "").strip()

                    data = json.loads(raw)
                    data["file_name"] = name
                    results.append(data)

                except Exception as e:
                    st.warning(f"❌ Failed to parse {name}: {str(e)}")

    # -------------------------------------------------
    # DISPLAY & DOWNLOAD
    # -------------------------------------------------
    if results:
        df = pd.DataFrame(results)
        st.success("✅ Resume analysis completed successfully!")
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV",
            csv,
            file_name="resume_analysis.csv",
            mime="text/csv"
        )

    else:
        st.error("❌ No valid resumes found in the ZIP file.")