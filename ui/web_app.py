import streamlit as st
from dotenv import load_dotenv
import os
import sys
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from app.parser import parse_docx
from app.transformer import convert_pega_to_servicenow
from app.formatter import save_to_docx

st.set_page_config(page_title="DesignShift AI", layout="wide")
st.title("📄 DesignShift AI: Convert Pega → ServiceNow")

uploaded_file = st.file_uploader("Upload your Pega Design Document (.docx)", type="docx")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    st.success("✅ Document uploaded successfully. Parsing...")

    sections = parse_docx(temp_path)
    st.subheader("📑 Extracted Sections")
    for title, content in sections.items():
        with st.expander(title):
            st.text_area(f"Pega: {title}", content, height=150)

    st.subheader("🔁 Converted Sections (ServiceNow)")
    converted = {}
    # print("🔐 OpenAI Key from env:", sections.items())
    for title, content in sections.items():
        with st.spinner(f"Converting '{title}'..."):
            converted_text = convert_pega_to_servicenow(title, content)
            converted[title] = converted_text
            st.text_area(f"ServiceNow: {title}", converted_text, height=150)

    output_file = "ServiceNow_Design.docx"
    save_to_docx(converted, output_file)
    with open(output_file, "rb") as f:
        st.download_button("📥 Download Converted DOCX", f, file_name=output_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
