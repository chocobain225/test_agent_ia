import os
import json
import re
from pathlib import Path
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# -----------------------
# Configuration API
# -----------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Veuillez définir GROQ_API_KEY dans .env")
client = Groq(api_key=GROQ_API_KEY)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
]

TOKEN_PATH = Path.home() / ".token.json"
CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "<VOTRE_CLIENT_ID>")
CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "<VOTRE_CLIENT_SECRET>")

# -----------------------
# Gestion des credentials
# -----------------------
def get_credentials():
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = {
                "installed": {
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds

# -----------------------
# Classification d'un email
# -----------------------
def classify_email(email_text):
    """
    Retourne un dict avec keys : category, type, summary
    """
    prompt = f"""
    Tu es un assistant qui classe des emails.
    Classe cet email en JSON avec les champs :
    - category : urgent / normal / info
    - type : type d'email (ex: facture, support, personnel, autre)
    - summary : résumé en une phrase
    Email : {email_text}
    """
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "Tu es un classifieur d'emails."},
            {"role": "user", "content": prompt}
        ]
    )
    content = resp.choices[0].message.content.strip()

    # Enlever ```json ... ``` si présent
    content = re.sub(r"```json\s*|\s*```", "", content, flags=re.IGNORECASE).strip()

    # Essayer de parser JSON
    try:
        data = json.loads(content)
        return {
            "category": data.get("category", "unknown"),
            "type": data.get("type", "unknown"),
            "summary": data.get("summary", "")
        }
    except json.JSONDecodeError:
        return {"category": "unknown", "type": "unknown", "summary": content}

# -----------------------
# Création d’un nouveau Google Sheet unique
# -----------------------
def create_new_sheet(drive_service):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sheet_name = f"Cheick"
    file_metadata = {'name': sheet_name, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    file = drive_service.files().create(body=file_metadata, fields='id').execute()
    sheet_id = file.get('id')
    print(f"✅ Nouveau Google Sheet créé : {sheet_name} (ID: {sheet_id})")
    return sheet_id

# -----------------------
# Main
# -----------------------
def main():
    creds = get_credentials()
    gmail_service = build("gmail", "v1", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Nouveau Google Sheet
    SHEET_ID = create_new_sheet(drive_service)

    # Gmail
    profile = gmail_service.users().getProfile(userId="me").execute()
    print("Compte connecté:", profile.get("emailAddress"))

    results = gmail_service.users().messages().list(userId="me", maxResults=50).execute()
    messages = results.get("messages", [])

    # Préparer les données
    rows = [["ID", "Snippet", "Category", "Type", "Summary"]]

    for m in messages:
        full_msg = gmail_service.users().messages().get(userId="me", id=m["id"]).execute()
        snippet = full_msg.get("snippet", "(pas de snippet)")
        classification = classify_email(snippet)

        rows.append([
            m["id"],
            snippet,
            classification["category"],
            classification["type"],
            classification["summary"]
        ])

    # Écrire les données dans le nouveau sheet
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SHEET_ID,
        range="A1",
        valueInputOption="RAW",
        body={"values": rows}
    ).execute()

    print("✅ Résultats écrits dans le nouveau Google Sheet")

if __name__ == "__main__":
    main()