# google_auth.py
from __future__ import annotations
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.oauth2.credentials
import os, json, pathlib

def get_credentials(scopes: list[str], creds_file: str = "credentials.json", token_file: str = "token.json"):
    """
    Retorna credenciais OAuth2 válidas para as SCOPES pedidas.
    Se não houver token, abre o navegador e salva em token.json.
    """
    token_path = pathlib.Path(token_file)
    creds = None

    if token_path.exists():
        creds = google.oauth2.credentials.Credentials.from_authorized_user_file(token_file, scopes=scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, scopes=scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return creds
