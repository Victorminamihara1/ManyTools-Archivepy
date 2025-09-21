# gmail_client.py
from __future__ import annotations
from base64 import urlsafe_b64encode, urlsafe_b64decode
from email.message import EmailMessage
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pathlib import Path
from google_auth import get_credentials
import mimetypes

# ---- SCOPES ----
SCOPE_READ = "https://www.googleapis.com/auth/gmail.readonly"
SCOPE_SEND = "https://www.googleapis.com/auth/gmail.send"
SCOPES_BOTH = [SCOPE_READ, SCOPE_SEND]

def _service():
    """Cria o service SEMPRE com ambos os escopos, evitando token 'magro'."""
    creds = get_credentials(scopes=SCOPES_BOTH)
    return build("gmail", "v1", credentials=creds)

# --------- DOWNLOAD DE ANEXOS XLSX ---------
def baixar_anexos_xlsx_google(query: str, destino_planilha_dir: str, max_results: int = 50) -> int:
    """
    Ex.: query = 'newer_than:7d has:attachment filename:xlsx'
    Salva .xlsx em destino_planilha_dir. Retorna contagem de anexos baixados.
    """
    svc = _service()
    Path(destino_planilha_dir).mkdir(parents=True, exist_ok=True)
    baixados = 0

    try:
        resp = svc.users().messages().list(userId="me", q=query, maxResults=max_results).execute()
        msgs = resp.get("messages", [])
        for m in msgs:
            msg = svc.users().messages().get(userId="me", id=m["id"], format="full").execute()

            # parts podem ser aninhadas; vamos varrer recursivamente
            stack = [(msg.get("payload", {}) or {})]
            while stack:
                part = stack.pop()
                if not isinstance(part, dict):
                    continue
                # se houver subpartes, empilha
                for sp in part.get("parts", []) or []:
                    stack.append(sp)

                filename = part.get("filename")
                body = part.get("body", {}) or {}
                if not filename or not filename.lower().endswith(".xlsx"):
                    continue

                att_id = body.get("attachmentId")
                if att_id:
                    att = svc.users().messages().attachments().get(
                        userId="me", messageId=m["id"], id=att_id
                    ).execute()
                    data_bytes = urlsafe_b64decode(att["data"].encode("utf-8"))
                else:
                    data_b64 = body.get("data")
                    if not data_b64:
                        continue
                    data_bytes = urlsafe_b64decode(data_b64.encode("utf-8"))

                out_path = Path(destino_planilha_dir) / filename
                with open(out_path, "wb") as f:
                    f.write(data_bytes)
                baixados += 1

    except HttpError as e:
        raise RuntimeError(f"Gmail API error ao baixar anexos: {e}")

    return baixados

# --------- ENVIAR E-MAIL (com anexo opcional) ---------
def enviar_email_google(remetente: str, destinatarios: list[str], assunto: str, corpo_texto: str, anexos: list[str] | None = None):
    svc = _service()

    msg = EmailMessage()
    msg["From"] = remetente
    msg["To"] = ", ".join(destinatarios)
    msg["Subject"] = assunto
    msg.set_content(corpo_texto)

    for path in (anexos or []):
        p = Path(path)
        ctype, _ = mimetypes.guess_type(p.name)
        maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
        with open(p, "rb") as f:
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=p.name)

    raw = urlsafe_b64encode(msg.as_bytes()).decode("utf-8")

    try:
        svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    except HttpError as e:
        raise RuntimeError(f"Gmail API error ao enviar: {e}")
