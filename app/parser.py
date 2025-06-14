from docx import Document

def parse_docx(file_path):
    doc = Document(file_path)
    sections = {}
    current_title = None
    current_content = []

    for para in doc.paragraphs:
        if para.style and para.style.name == 'Heading 1' and para.text.strip():
            if current_title:
                sections[current_title] = "\n".join(current_content).strip()
            current_title = para.text.strip()
            current_content = []
        elif para.text.strip():
            current_content.append(para.text.strip())

    if current_title and current_content:
        sections[current_title] = "\n".join(current_content).strip()

    return sections
