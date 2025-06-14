from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def convert_pega_to_servicenow(title, content):
    # print("🔐 OpenAI Key from env:", api_key)
    if not content.strip():
        return "⚠️ No content to convert."

    prompt = f"""You are an expert in Pega and ServiceNow. Convert the following Pega design section into an equivalent ServiceNow design section.

Title: {title}
Content:
{content}

Output:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[
                {"role": "system", "content": "You are a helpful assistant converting design documents from Pega to ServiceNow."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        print(response.choices[0].message);
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API Error: {str(e)}"
