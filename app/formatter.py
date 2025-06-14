from docx import Document

def save_to_docx(sections_dict, output_path):
    doc = Document()
    for title, content in sections_dict.items():
        doc.add_heading(title, level=1)
        for line in content.split('\n'):
            doc.add_paragraph(line)
    doc.save(output_path)
