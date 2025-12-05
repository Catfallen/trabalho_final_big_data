import os
import requests
from dotenv import load_dotenv

load_dotenv()

MANUS_API_KEY = os.getenv("MANUS_API_KEY")

MANUS_URL = "https://api.manus.ai/v1/tasks"
MANUS_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "API_KEY": MANUS_API_KEY
}


def manus_post(prompt: str, agent: str = "manus-1.5-lite") -> dict:
    print("Iniciando")
    """
    Envia um prompt para o Manus AI e retorna o JSON da resposta.

    :param prompt: Texto completo do prompt a ser enviado
    :param agent: Perfil do agente (manus-1.5 ou manus-1.5-lite)
    :return: dicionário JSON com a resposta do Manus
    """
    payload = {
        "prompt": prompt,
        "agentProfile": agent
    }

    try:
        response = requests.post(MANUS_URL, json=payload, headers=MANUS_HEADERS)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("Erro ao acessar Manus API:", e)
        return {"error": str(e)}
    
    

import requests


def manus_get(task_id):
    url = f"{MANUS_URL}/{task_id}"

    headers = {"API_KEY": MANUS_API_KEY}

    response = requests.get(url, headers=headers)

    # apenas para debug
    print("GET STATUS:", response.status_code)

    try:
        data = response.json()     # ← transforma em dict
    except Exception:
        print("ERRO AO PARSER JSON:", response.text)
        return None

    return data                   # ← retorna dict