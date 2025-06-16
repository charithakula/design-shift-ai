import streamlit as st
from dotenv import load_dotenv
import os
import sys
import tempfile
from openai import OpenAI

from login import login

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

from admin import admin_panel  
from app.parser import parse_docx
from app.formatter import save_to_docx, insert_images_to_docx
from app.transformer import detect_technology_from_text, convert_any_to_any
from app.image_utils import extract_images_from_docx, analyze_and_convert_diagram
from app.diagram_handler import regenerate_diagram_from_text

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OpenAI API key is not set. Please set OPENAI_API_KEY in your environment.")
    st.stop()

client = OpenAI(api_key=api_key)

if "page" not in st.session_state:
    st.session_state.page = "main"

# Uncomment below if login flow should be active
login()

with st.sidebar:
    st.markdown("## 📂 Navigation")

    if st.session_state.get("authenticated", False) or st.session_state.get("admin_authenticated", False):
        if st.button("🔓 Logout"):
            st.session_state.page = "main"
            for key in [
                "authenticated", "username", "role",
                "admin_authenticated", "admin_username",
                "admin_username_input", "admin_password_input",
                "suggested_custom_techs",
            ]:
                st.session_state.pop(key, None)
            st.experimental_rerun()

        if st.button("🏠 Main Page"):
            st.session_state.page = "main"

        if st.session_state.get("role") == "admin" or st.session_state.get("admin_authenticated"):
            if st.button("🔧 Go to Admin Settings"):
                st.session_state.page = "admin"

if st.session_state.page == "admin":
    admin_panel()
    st.stop()

st.title("📄 Design Document Converter")

# --- Upload and detect source tech ---

uploaded_file = st.file_uploader("Upload your Design Document (.docx)", type="docx")
detected_source_tech = None

if uploaded_file:
    file_bytes = uploaded_file.read()
    st.session_state['uploaded_file'] = file_bytes
    st.session_state['uploaded_file_name'] = uploaded_file.name

    # Create temp file for processing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(file_bytes)
        temp_path = tmp_file.name

    try:
        sections = parse_docx(temp_path)
        full_text = "\n".join([sec.get("content", "") for sec in sections])
        detected_source_tech = detect_technology_from_text(full_text, client)
        st.session_state['detected_source_tech'] = detected_source_tech
        st.session_state['sections'] = sections
        st.session_state['temp_docx_path'] = temp_path

        st.success(f"Detected Source Technology: {detected_source_tech}")
    except Exception as e:
        st.error(f"Error processing document: {e}")

# --- Target technology selection ---

target_tech_options = ["Pega", "ServiceNow", "Salesforce", "SAP", "Power Platforms", "CustomTech"]
target_tech = st.selectbox("Select Target Technology", options=target_tech_options, index=0)

# CustomTech suggestions block
suggested_custom_techs = []

if target_tech == "CustomTech" and detected_source_tech:
    if st.button("Get Suggested Technologies"):
        with st.spinner("Getting suggestions from OpenAI..."):
            try:
                prompt = (
                    f"I have a design document written for technology '{detected_source_tech}'. "
                    "Suggest 3 to 5 target technologies appropriate for converting this design document. "
                    "List them as a comma separated list."
                )
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.7,
                )
                suggestions_text = response.choices[0].message.content.strip()
                suggested_custom_techs = [s.strip() for s in suggestions_text.split(",") if s.strip()]
                st.session_state['suggested_custom_techs'] = suggested_custom_techs
            except Exception as e:
                st.error(f"OpenAI API Error: {e}")

if 'suggested_custom_techs' in st.session_state and st.session_state['suggested_custom_techs']:
    st.write("### Suggested Target Technologies:")
    chosen_tech = st.selectbox(
        "Choose one of the suggested target technologies or enter your own:",
        options=st.session_state['suggested_custom_techs'] + ["Other"]
    )
    if chosen_tech == "Other":
        custom_tech_input = st.text_input("Enter Custom Technology Name")
    else:
        custom_tech_input = chosen_tech
else:
    custom_tech_input = None

# Determine final target tech to use
final_target_tech = custom_tech_input if custom_tech_input else (target_tech if target_tech != "CustomTech" else None)

# --- Conversion process ---

can_convert = (
    (uploaded_file is not None or 'uploaded_file' in st.session_state) 
    and final_target_tech is not None and final_target_tech != ""
)

if can_convert:
    if st.button("Convert Document"):
        sections = st.session_state.get('sections', [])
        detected_source_tech = st.session_state.get('detected_source_tech', 'Unknown')
        temp_docx_path = st.session_state.get("temp_docx_path")

        if not sections:
            st.error("No document sections found to convert.")
            st.stop()

        st.info(f"Converting from {detected_source_tech} to {final_target_tech}")

        converted = {}
        try:
            for section in sections:
                title = section.get("title", "Untitled")
                converted_text = convert_any_to_any(section, detected_source_tech, final_target_tech, client)
                converted[title] = converted_text
        except Exception as e:
            st.error(f"Error during conversion: {e}")
            st.stop()

        st.session_state['converted'] = converted

        # Diagram extraction + regeneration
        if temp_docx_path and os.path.exists(temp_docx_path):
            st.info("📊 Checking and updating flow diagrams...")
            try:
                diagrams = extract_images_from_docx(temp_docx_path)
                st.write(f"Extracted {len(diagrams)} diagram(s) from document.")
                regenerated_diagrams = []

                for image_bytes, image_name in diagrams:
                    st.write(f"Processing diagram: {image_name}")
                    description = analyze_and_convert_diagram(
                        image_bytes, detected_source_tech, final_target_tech, client
                    )
                    st.write(f"Diagram description: {description}")

                    diagram_image_path = regenerate_diagram_from_text(
                        description, final_target_tech, client
                    )

                    if diagram_image_path and os.path.exists(diagram_image_path):
                        st.write(f"Diagram generated and saved to: {diagram_image_path}")
                        regenerated_diagrams.append(diagram_image_path)
                    else:
                        st.warning(f"Failed to generate diagram for {image_name}")

                st.session_state['diagrams'] = regenerated_diagrams

                # ===== NEW BLOCK: Display and Download Generated Diagrams =====
                if 'diagrams' in st.session_state and st.session_state['diagrams']:
                    st.subheader("🖼️ Generated Diagrams")
                    for diagram_path in st.session_state['diagrams']:
                        if os.path.exists(diagram_path):
                            with open(diagram_path, "rb") as img_file:
                                st.image(diagram_path, caption=os.path.basename(diagram_path), use_column_width=True)
                                st.download_button(
                                    label=f"📥 Download {os.path.basename(diagram_path)}",
                                    data=img_file,
                                    file_name=os.path.basename(diagram_path),
                                    mime="image/png"
                                )
                        else:
                            st.warning(f"Diagram image not found: {diagram_path}")
                # =============================================================

            except Exception as e:
                st.error(f"Error processing diagrams: {e}")
        else:
            st.warning("Temporary DOCX file not found, skipping diagram extraction.")

        # Save converted content + images to DOCX
        output_file = f"{final_target_tech}_Design.docx"
        try:
            insert_images_to_docx(output_file, st.session_state['converted'], st.session_state.get('diagrams', []))
            st.session_state['output_file'] = output_file
            st.success(f"Conversion complete! File saved as {output_file}")
        except Exception as e:
            st.error(f"Error saving converted document: {e}")

        # Cleanup temp file after processing
        try:
            if temp_docx_path and os.path.exists(temp_docx_path):
                os.remove(temp_docx_path)
        except Exception:
            pass

# --- Show original sections ---

if 'sections' in st.session_state:
    st.subheader(f"📑 Extracted Sections from {st.session_state.get('detected_source_tech', 'Unknown')}")
    for section in st.session_state['sections']:
        st.expander(section.get("title", "Untitled")).text_area("Original", section.get("content", ""), height=150)

# --- Show converted sections ---

if 'converted' in st.session_state:
    st.subheader(f"🔁 Converted Sections to {final_target_tech}")
    for title, content in st.session_state['converted'].items():
        st.expander(title).text_area("Converted", content, height=150)

# --- Download button ---

if 'output_file' in st.session_state:
    output_file = st.session_state['output_file']
    try:
        with open(output_file, "rb") as f:
            st.download_button(
                f"📥 Download Converted {final_target_tech} DOCX", f,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
    except FileNotFoundError:
        st.error("Converted file not found. Please convert the document again.")
else:
    st.info("Please upload a document to enable conversion.")
