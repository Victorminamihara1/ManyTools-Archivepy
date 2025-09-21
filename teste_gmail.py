from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
creds = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES).run_local_server(port=0)
svc = build("gmail","v1",credentials=creds)
print(svc.users().messages().list(userId="me", maxResults=1).execute().get("resultSizeEstimate",0))
