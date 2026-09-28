import os
import requests

from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

router = APIRouter()

API_KEY = os.getenv("GEMINI_API_KEY")


class DocumentRequest(BaseModel):
    document_type: str
    parties: str = ""
    terms: str = ""
    dates: str = ""


@router.post("/generate")
def generate_document(request: DocumentRequest):

    if not API_KEY:
        return {
            "error": "GEMINI_API_KEY is missing from .env"
        }

    prompt = f"""
You are LegalEase, an AI-assisted legal document drafting system.

Create a professional legal document draft.

DOCUMENT TYPE:
{request.document_type}

PARTIES:
{request.parties}

TERMS AND CONDITIONS:
{request.terms}

DATES:
{request.dates}

INSTRUCTIONS:

1. Create a complete and professionally structured legal document.
2. Use clear and formal legal language.
3. Add an appropriate title.
4. Add relevant sections and clauses.
5. Do not invent facts.
6. If information is missing, write [TO BE FILLED].
7. Include signature sections where appropriate.
8. Organize the document logically.
9. Add a short notice saying the document should be reviewed
   by a qualified legal professional before use.

Generate only the legal document and review notice.
"""

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-3.8-flash:generateContent"
        "?key=" + API_KEY
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return {
                "error": (
                    "Gemini API Error: "
                    + str(response.status_code)
                    + "\n\n"
                    + response.text
                )
            }

        data = response.json()

        candidates = data.get("candidates", [])

        if not candidates:
            return {
                "error": "Gemini returned no response."
            }

        parts = candidates[0].get(
            "content", {}
        ).get("parts", [])

        if not parts:
            return {
                "error": "Gemini returned an empty response."
            }

        generated_text = parts[0].get("text", "")

        if not generated_text:
            return {
                "error": "Generated document is empty."
            }

        return {
            "document": generated_text
        }

    except requests.exceptions.RequestException as error:

        return {
            "error": "Could not connect to Gemini: " + str(error)
        }

    except Exception as error:

        return {
            "error": "Unexpected error: " + str(error)
        }