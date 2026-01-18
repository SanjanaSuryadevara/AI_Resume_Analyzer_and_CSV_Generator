
# 📄 AI-Powered Resume Analyzer & CSV Generator

## Overview
This project automates bulk resume analysis using LangChain and LLMs.
Upload a ZIP file containing resumes and receive a structured CSV output.

## Features
- ZIP upload of resumes
- PDF & DOCX parsing
- Structured extraction using TypedDictOutputParser
- CSV download via Streamlit

## Setup
```bash
pip install -r requirements.txt
```
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_key_here
```

Run:
```bash
streamlit run main.py
```
