import pytesseract
from PIL import Image
import io
import uuid
import graphviz
from docx import Document

def extract_images_from_docx(docx_path):
    doc = Document(docx_path)
    images = []

    for rel in doc.part._rels:
        rel_obj = doc.part._rels[rel]
        if "image" in rel_obj.target_ref:
            image_data = rel_obj.target_part.blob
            images.append(image_data)  # Keep image bytes, no file write here

    return images

def extract_text_from_image(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"OCR failed: {e}"

def regenerate_diagram_from_text(text_description, final_target_tech, client):
    prompt = (
        f"The following is a diagram description for a system built using {final_target_tech}:\n\n"
        f"{text_description}\n\n"
        f"Generate only the diagram in valid Graphviz DOT format. "
        f"Do not include any comments, code fences, or explanations. Only return valid DOT."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=400,
        )
        dot_code = response.choices[0].message.content.strip()

        # Debugging
        print("---- DOT CODE GENERATED ----")
        print(dot_code)
        print("----------------------------")

        # Remove any ```dot or ``` wrappers
        if dot_code.startswith("```"):
            lines = dot_code.splitlines()
            lines = [line for line in lines if not line.strip().startswith("```")]
            dot_code = "\n".join(lines)

        # Validate DOT
        if not ("digraph" in dot_code or "graph" in dot_code):
            raise ValueError("Invalid DOT format: missing 'graph' or 'digraph' keyword.")

        return render_dot_to_image(dot_code)

    except Exception as e:
        print(f"Diagram generation failed: {e}")
        return None

def render_dot_to_image(dot_code):
    try:
        dot = graphviz.Source(dot_code)
        filename = f"generated_diagram_{uuid.uuid4().hex[:8]}"
        output_path = dot.render(filename, format="png", cleanup=True)
        return output_path
    except Exception as e:
        print(f"Graphviz rendering failed: {e}")
        return None