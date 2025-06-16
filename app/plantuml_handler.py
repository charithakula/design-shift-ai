import subprocess
import uuid
import os

def generate_plantuml_diagram(uml_text: str, output_format: str = "png") -> str:
    """
    Generate a PlantUML diagram from UML text and save as PNG or SVG.
    Returns the filepath of generated image or None on failure.
    """
    temp_id = uuid.uuid4().hex[:8]
    uml_file = f"plantuml_{temp_id}.puml"
    output_file = f"plantuml_{temp_id}.{output_format}"

    with open(uml_file, "w") as f:
        f.write(uml_text)

    try:
        # Assuming plantuml.jar is in your project root or adjust path
        subprocess.run([
            "java", "-jar", "plantuml.jar",
            f"-t{output_format}", uml_file
        ], check=True)
        if os.path.exists(output_file):
            return output_file
        else:
            return None
    except Exception as e:
        print(f"PlantUML generation error: {e}")
        return None
    finally:
        if os.path.exists(uml_file):
            os.remove(uml_file)
