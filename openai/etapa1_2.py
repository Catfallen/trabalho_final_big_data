import pandas as pd
from pathlib import Path
import re
from Levenshtein import distance as lev
from conn import manus_post,manus_get
from prompt import get_prompt
from time import sleep
import ast
import json
#import requests
# ------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------

PREPOSICOES = {"de", "da", "do", "das", "dos", "a", "o", "na", "no"}



def extrair_dict_valido(texto):
    # Captura qualquer trecho entre { e }
    matches = re.findall(r"\{[\s\S]*?\}", texto)

    candidatos = []

    # Tentamos converter cada match
    for m in matches:
        try:
            d = ast.literal_eval(m)
            if isinstance(d, dict):
                candidatos.append((len(m), d))  # guardar tamanho para escolher o maior
        except:
            continue

    if not candidatos:
        raise ValueError("Nenhum dicionário válido encontrado na resposta da IA")

    # Retorna o maior dicionário encontrado
    candidatos.sort(reverse=True)
    return candidatos[0][1]



def extract_response_text(result):
    if "output" not in result:
        return None
    
    texts = []
    for block in result["output"]:
        if "content" not in block:
            continue
        for item in block["content"]:
            if item.get("type") == "output_text":
                texts.append(item.get("text"))
    
    return "\n".join(texts)

import re

def extract_only_dict(text):
    # encontra o dicionário Python entre chaves
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return None



def normalizar_verbo(texto: str) -> str:
    """
    Normaliza o verbo:
    - minúsculas
    - remove preposições depois do verbo
    - remove plurais simples
    """
    texto = texto.lower().strip()
    palavras = texto.split()

    if not palavras:
        return texto

    verbo = palavras[0]

    # Se segunda palavra for preposição → ignora
    if len(palavras) > 1 and palavras[1] in PREPOSICOES:
        return verbo

    return verbo


def similaridade(a, b):
    """similaridade normalizada entre 0 e 1"""
    d = lev(a, b)
    return 1 - d / max(len(a), len(b))


def agrupar_centro_fixo(palavras, limiar=0.80):
    """
    Agrupa palavras semelhantes SEM efeito-cadeia.
    Cada grupo tem um centro fixo (a primeira palavra).
    Nova palavra só entra se for similar ao centro.
    """
    grupos = []

    for palavra in palavras:
        colocada = False

        for grupo in grupos:
            centro = grupo[0]  # centro do grupo

            # primeira letra deve coincidir
            if palavra[0] != centro[0]:
                continue

            # similaridade com o centro
            if similaridade(palavra, centro) >= limiar:
                grupo.append(palavra)
                colocada = True
                break

        if not colocada:
            grupos.append([palavra])

    return grupos



# ------------------------------------------------------
# CARREGA CSV E EXTRAI VERBOS
# ------------------------------------------------------

caminho = Path("saida.csv")
df = pd.read_csv(caminho, sep=";")

df["DescricaoManutencao"] = (
    df["DescricaoManutencao"]
    .astype(str)
    .str.strip()
)

df = df[df["DescricaoManutencao"] != ""]

# Extrai verbo inicial normalizado
verbos = set()

for descricao in df["DescricaoManutencao"]:
    palavras = descricao.lower().split()
    if not palavras:
        continue

    verbo = normalizar_verbo(descricao)
    verbos.add(verbo)

verbos = list(sorted(verbos))

# ------------------------------------------------------
# AGRUPAMENTO ETAPA 1
# ------------------------------------------------------

grupos = agrupar_centro_fixo(verbos, limiar=0.80)

# ------------------------------------------------------
# EXIBE RESULTADO
# ------------------------------------------------------

print("\n===== GRUPOS DA ETAPA 1 =====\n")
for g in grupos:
    print(g)


prompt = get_prompt(grupos)

response = manus_post(prompt)
print(response)

while True:
    sleep(3)
    result = manus_get(response.get('task_id'))
    if result.get("status") == "completed":
        
        break
    print("Ainda processando... aguardando 2s")
    sleep(2)
print("JSON COMPLETO:", result)
response_text = extract_response_text(result)
print("===")
print(response_text)


inicio = response_text.rfind("{")
fim = response_text.rfind("}")

print("===Only dict===")


dicionario = extrair_dict_valido(response_text)


# Converte para dict
#dicionario = ast.literal_eval(dicionario_str)


with open("dicionario.json", "w", encoding="utf-8") as f:
    json.dump(dicionario, f, ensure_ascii=False, indent=4)

print("JSON salvo com sucesso!")




