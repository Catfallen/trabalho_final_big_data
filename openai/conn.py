import os
import requests
from dotenv import load_dotenv

load_dotenv()

MANUS_API_KEY = os.getenv("MANUS_API_KEY")

url = "https://api.manus.ai/v1/tasks"
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "API_KEY": f"{MANUS_API_KEY}"
}

# Corrigido: usar 'agentProfile' em vez de 'mode'
data = {
    "prompt": "hello",
    "agentProfile": "manus-1.5-lite"  # Opções: manus-1.5, manus-1.5-lite
}

response = requests.post(url, json=data, headers=headers)
print(response.json())