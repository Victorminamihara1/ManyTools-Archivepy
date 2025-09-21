# enviar_confirmacao.py
from pathlib import Path
from gmail_client import enviar_email_google

def enviar_confirmacao(relatorio_txt: str, remetente: str, destinatarios: list[str], assunto: str = "Fechamento de Caixa — Confirmação"):
    corpo = Path(relatorio_txt).read_text(encoding="utf-8")
    enviar_email_google(
        remetente=remetente,
        destinatarios=destinatarios,
        assunto=assunto,
        corpo_texto=corpo,
        anexos=[relatorio_txt],
    )