
import os
import re
import pandas as pd
import docx
import PyPDF2
import streamlit as st
import zipfile
import io
import base64
import time
import tempfile
import shutil
import subprocess

# === CONFIGURATION ===
BASE_PATH = os.path.dirname(__file__)
FAKE_COMPANY_LIST_PATH = os.path.join(BASE_PATH, "fake_companies.xlsx")
GENUINE_OUTPUT = os.path.join(BASE_PATH, "Genuine_Results.xlsx")
FAKE_OUTPUT = os.path.join(BASE_PATH, "Fake_Results.xlsx")
TEMP_DIR = os.path.join(BASE_PATH, "temp_files")
os.makedirs(TEMP_DIR, exist_ok=True)

# === TEXT EXTRACTORS ===
def extract_text_from_docx(file_path):
    try:
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error reading DOCX: {e}")
        return ""

def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            return "\n".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return ""

def extract_text_from_doc(file_path):
    if shutil.which("soffice") is None:
        st.error("LibreOffice (soffice) is not installed or not in PATH.")
        return ""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["soffice", "--headless", "--convert-to", "txt:Text", "--outdir", tmpdir, file_path], check=True)
            base = os.path.splitext(os.path.basename(file_path))[0]
            txt_path = os.path.join(tmpdir, base + ".txt")
            with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception as e:
        st.error(f"Error extracting DOC: {e}")
        return ""

# === LOAD FAKE COMPANIES FROM EXCEL ===
def load_fake_companies():
    df = pd.read_excel(FAKE_COMPANY_LIST_PATH, usecols=[0])
    return df.iloc[:, 0].dropna().astype(str).str.strip().str.lower().tolist()

# === NORMALIZATION ===
def normalize(s):
    return re.sub(r"[^\w\s]", "", s).lower().strip()

# === DETECTION ===
def is_fake_resume(text, fake_list):
    lines = text.splitlines()
    fake_set = set(map(normalize, fake_list))
    delimiters = [',', ';', ' at ', ' with ', ' in ', '|', 'joined', 'organization',
                  'experience', 'worked', 'working', 'currently', 'employer', 'company',
                  'firm', 'served', 'project']
    def split_line(line):
        for d in delimiters:
            line = line.replace(d, '|')
        return [e.strip() for e in line.split('|') if e.strip()]
    for line in lines:
        for entity in split_line(line):
            if normalize(entity) in fake_set:
                return True, entity, line.strip()
    return False, "", ""

# === SAVE TO EXCEL ===
def save_result_to_excel(df, path):
    if os.path.exists(path):
        try:
            existing = pd.read_excel(path)
            df = pd.concat([existing, df], ignore_index=True)
        except zipfile.BadZipFile:
            pass
    df.to_excel(path, index=False)

# === CUSTOM CSS ===
st.markdown("""
     <style>
     [data-testid="stWidgetLabel"] {
         color: rgb(214, 26, 96) !important;
         font-weight: bold;
     }

     [data-testid="stBaseButton-secondary"] {
         color: white;
         background-color: green;
     }

     [data-testid="stBaseButton-secondary"]:hover {
         color: white;
         background-color: #2eba2e;
         border: white;
     }

     [data-testid="stFileUploaderDropzoneInstructions"] svg {
         fill: green;
     }

     /* Main Title and Subtitle */
     .title-text {
         text-align: center;
         font-size: 42px;
         font-weight: bold;
         color: #2C5282;
         margin-bottom: 0.2em;
     }

     .subtitle-text {
         text-align: center;
         font-size: 20px;
         color: #718096;
         margin-bottom: 2em;
     }

     /* Upload label */
     label[data-testid="stFileUploaderLabel"] {
         color: #4A5568 !important;
         font-size: 1rem !important;
         font-weight: 500 !important;
     }

     /* Drag-and-drop area */
     section[data-testid="stFileUploadDropzone"] {
         background-color: #000000 !important;
         border: 1px solid #E2E8F0 !important;
         border-radius: 0.5rem !important;
     }

     section[data-testid="stFileUploadDropzone"] * {
         color: #4A5568 !important;
     }

     /* "Browse files" button */
     button[title="Browse files"] {
         background-color: #FFFFFF !important;
         color: #4A5568 !important;
         border: 1px solid #E2E8F0 !important;
         border-radius: 0.5rem !important;
     }

     button[title="Browse files"]:hover {
         background-color: #F7FAFC !important;
         color: #2D3748 !important;
         border-color: #CBD5E0 !important;
     }

     /* Table and download link styles */
     .custom-table {
         font-family: 'Segoe UI', Arial, sans-serif;
         font-size: 16px;
         border-collapse: collapse;
         width: 100%;
         table-layout: auto;
         box-shadow: 0 2px 8px rgba(0,0,0,0.04);
     }

     .custom-table th, .custom-table td {
         border: 1px solid #ddd;
         padding: 12px 10px;
         text-align: left;
         vertical-align: top;
         max-width: 320px;
         word-break: break-word;
         white-space: pre-line;
     }

     .custom-table th {
         background-color: transparent !important;
         color: #2C5282 !important;
         font-weight: bold !important;
         white-space: nowrap !important;
     }

     .custom-table td:hover, .custom-table th:hover {
         background-color: #C6F6D5 !important;
     }

     .custom-table tr:hover {
         background-color: #F7FAFC;
     }

     .tao-logo-absolute {
         position: fixed;
         top: 0;
         left: 0;
         width: 180px;
         z-index: 9999;
     }

     .download-zip-btn {
         background-color: #EBF8FF !important;
         color: #2C5282 !important;
         border: 1px solid #BEE3F8 !important;
         border-radius: 8px !important;
         font-weight: 600 !important;
         padding: 10px 18px !important;
         font-size: 1rem !important;
         margin-top: 10px;
         margin-bottom: 10px;
         box-shadow: 0 2px 8px rgba(44,82,130,0.04);
         transition: background 0.2s, color 0.2s;
     }

     .download-zip-btn:hover {
         background-color: #BEE3F8 !important;
         color: #2C5282 !important;
     }

     button[data-testid="baseButton-download-zip-btn-real"] {
         background-color: #EBF8FF !important;
         color: #2C5282 !important;
         border: 1px solid #BEE3F8 !important;
         border-radius: 8px !important;
         font-weight: 600 !important;
         padding: 10px 18px !important;
         font-size: 1rem !important;
         margin-top: 10px;
         margin-bottom: 10px;
         box-shadow: 0 2px 8px rgba(44,82,130,0.04);
         transition: background 0.2s, color 0.2s;
     }

     button[data-testid="baseButton-download-zip-btn-real"]:hover {
         background-color: #BEE3F8 !important;
         color: #2C5282 !important;
     }

     .genuine-title {
         font-size: 1.5rem;
         font-weight: bold;
         color: #2C5282;
         display: flex;
         align-items: center;
         margin-bottom: 0.5em;
     }
     </style>
     <img src='https://i.postimg.cc/GtzH6R0W/image.jpg' class='tao-logo-absolute' />
 """, unsafe_allow_html=True)

# === STREAMLIT UI ===
st.markdown('<div class="title-text">Resume Validator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Fake Company Detection</div>', unsafe_allow_html=True)

uploaded_files = st.file_uploader("Upload Resume(s)", type=["pdf", "docx", "doc"], accept_multiple_files=True)

if uploaded_files:
    fake_list = load_fake_companies()
    fake_rows, genuine_rows = [], []

    for uploaded_file in uploaded_files:
        filename = uploaded_file.name
        ext = filename.split('.')[-1].lower()
        temp_path = os.path.join(TEMP_DIR, filename)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if ext == "pdf":
            text = extract_text_from_pdf(temp_path)
        elif ext == "docx":
            text = extract_text_from_docx(temp_path)
        elif ext == "doc":
            with st.spinner(f"Processing {filename}..."):
                text = extract_text_from_doc(temp_path)
        else:
            st.warning(f"Unsupported file format: {filename}")
            continue

        is_fake, matched_company, matched_line = is_fake_resume(text, fake_list)
        if is_fake:
            fake_rows.append({"Resume": filename, "Matched Fake Company": matched_company, "Line": matched_line, "Result": "FAKE"})
        else:
            genuine_rows.append({"Resume": filename, "Result": "GENUINE"})

        try: os.remove(temp_path)
        except: pass

    if fake_rows:
        df_fake = pd.DataFrame(fake_rows)
        st.markdown("### ❌ Fake Resumes")
        st.dataframe(df_fake)
        save_result_to_excel(df_fake, FAKE_OUTPUT)

    if genuine_rows:
        df_genuine = pd.DataFrame(genuine_rows)
        st.markdown("### ✅ Genuine Resumes")
        st.dataframe(df_genuine)
        save_result_to_excel(df_genuine, GENUINE_OUTPUT)

        genuine_files = [f for f in uploaded_files if f.name in {r['Resume'] for r in genuine_rows}]
        if len(genuine_files) == 1:
            f = genuine_files[0]
            b64 = base64.b64encode(f.getvalue()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="{f.name}">{f.name}</a>'
            st.markdown(href, unsafe_allow_html=True)
        elif len(genuine_files) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as zip_file:
                for f in genuine_files:
                    zip_file.writestr(f.name, f.getvalue())
            st.download_button("Download All Genuine Resumes as ZIP", data=zip_buffer.getvalue(), file_name="genuine_resumes.zip", mime="application/zip", key="download-zip-btn-real")
