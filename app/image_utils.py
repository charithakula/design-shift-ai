import base64
import io
import uuid
from docx import Document
from PIL import Image


def extract_images_from_docx(docx_path):
        """
        Extract images from a DOCX file.

        Args:
            docx_path (str): Path to the DOCX file.

        Returns:
            list of tuples: Each tuple contains (image_bytes, image_name).
        """
        doc = Document(docx_path)
        image_list = []

        for rel in doc.part._rels:
            rel_obj = doc.part._rels[rel]
            if "image" in rel_obj.target_ref:
                image_data = rel_obj.target_part.blob
                image_name = f"image_{uuid.uuid4().hex[:8]}.png"
                image_list.append((image_data, image_name))

        return image_list


def analyze_and_convert_diagram(image_bytes, source_tech, target_tech, client):
        """
        Analyze a diagram image and get a conversion description from the OpenAI client.

        Args:
            image_bytes (bytes): Image data in bytes.
            source_tech (str): Source technology name.
            target_tech (str): Target technology name.
            client: OpenAI API client instance.

        Returns:
            str: The assistant’s response describing the converted design.
        """
        image = Image.open(io.BytesIO(image_bytes))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        buffered.seek(0)

        # Proper base64 encoding
        image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        prompt = (
            f"This is a diagram from a {source_tech} design document. "
            f"Analyze it and describe how it would be implemented in {target_tech}."
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + image_b64}}
                    ],
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content