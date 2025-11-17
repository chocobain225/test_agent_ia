from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_APY_KEY"))

resp = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {"role": "system", "content": "Tu es un classifieur d'emails."},
        {"role": "user", "content": "Voici un email : ..."}
    ]
)

print(resp.choices[0].message["content"])