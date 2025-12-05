import pandas as pd
import re
from pathlib import Path
from rapidfuzz.distance import Levenshtein
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer


# ------------------------------------------------------
# Função para normalizar e pegar somente a ação principal
# ------------------------------------------------------
def extrair_acao(descricao: str):
    descricao = descricao.lower().strip()
    palavras = descricao.split()

    if not palavras:
        return ""

    # primeira palavra (ação principal)
    verbo = palavras[0]

    # ignorar números e sufixos como "4º"
    verbo = re.sub(r'\d+.*$', '', verbo)

    return verbo.strip()


# ------------------------------------------------------
# Agrupamento com vizinhos (vantagem: evita O(n²))
# ------------------------------------------------------
def agrupar_vizinhos(verbos, threshold=2):
    # Ordenar para aproximar palavras semelhantes
    verbos = sorted(list(verbos))

    grupos = {}
    grupo_atual = []
    ultimo = None

    for verbo in verbos:
        if ultimo is None:
            grupo_atual = [verbo]
            ultimo = verbo
            continue

        dist = Levenshtein.distance(verbo, ultimo)

        if dist <= threshold:
            grupo_atual.append(verbo)
        else:
            # salva grupo
            chave = grupo_atual[0]
            grupos[chave] = grupo_atual
            grupo_atual = [verbo]

        ultimo = verbo

    # adicionar último grupo
    if grupo_atual:
        chave = grupo_atual[0]
        grupos[chave] = grupo_atual

    return grupos


# ------------------------------------------------------
# Junta grupos equivalentes (ex: substituir + substituição)
# ------------------------------------------------------
def unir_grupos_por_stem(grupos):
    novo = {}

    def stem(p):
        # raiz comum para "substituir", "substituição", "subistituir"
        return re.sub(r'(ção|cao|sao|r|ar|er|ir)$', '', p)

    for chave, lista in grupos.items():
        raiz = stem(chave)

        if raiz not in novo:
            novo[raiz] = []

        novo[raiz].extend(lista)

    # Ordenar listas internas e criar chave final mais limpa
    final = {}
    for raiz, itens in novo.items():
        itens = sorted(set(itens))
        chave_final = itens[0]
        final[chave_final] = itens

    return final


# ------------------------------------------------------
# 1. CARREGA CSV
# ------------------------------------------------------
def processar_csv(caminho: str):
    caminho = Path(caminho)

    if not caminho.exists():
        raise FileNotFoundError("Arquivo CSV não encontrado.")

    df = pd.read_csv(caminho, sep=";")
    df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
    df = df[df["DescricaoManutencao"] != ""]

    # ------------------------------------------------------
    # 2. Extrair ação principal
    # ------------------------------------------------------
    verbos = set(df["DescricaoManutencao"].apply(extrair_acao))
    verbos.discard("")

    # ------------------------------------------------------
    # 3. Agrupar por vizinhança com Levenshtein
    # ------------------------------------------------------
    grupos_vizinhos = agrupar_vizinhos(verbos, threshold=2)

    # ------------------------------------------------------
    # 4. Unir grupos equivalentes (ex.: substituir/substituição)
    # ------------------------------------------------------
    grupos_finais = unir_grupos_por_stem(grupos_vizinhos)

    result = agrupar_sinonimos_semanticos(grupos_finais)
    print(result)
    return grupos_finais

def agrupar_sinonimos_semanticos(grupos_leven, distancia=1.0):
    """
    grupos_leven = resultado do Levenshtein:
      Ex:
        {
            "substituir": ["subistituir","substituir","substituicao"],
            "trocar": ["trocar","troca","trokcar"],
            ...
        }

    distancia = limiar para juntar sinônimos
    """

    # ------------------------------------------------------
    # 1. GERAR LISTA COMPLETA DE RÓTULOS
    # ------------------------------------------------------
    # incluir todas as variantes como elementos independentes
    todos_rotulos = set()
    for chave, variantes in grupos_leven.items():
        todos_rotulos.add(chave)
        for v in variantes:
            todos_rotulos.add(v)

    todos_rotulos = sorted(todos_rotulos)

    # carregar embeddings
    modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = modelo.encode(todos_rotulos, convert_to_numpy=True, normalize_embeddings=True)

    # ------------------------------------------------------
    # 2. AGRUPAMENTO SEMÂNTICO
    # ------------------------------------------------------
    cluster = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distancia,
        metric="cosine",
        linkage="average"
    )
    grupos_ids = cluster.fit_predict(embeddings)

    # ------------------------------------------------------
    # 3. MONTAR GRUPOS (SEM CHAVE PRINCIPAL)
    # ------------------------------------------------------
    grupos_semanticos = {}
    for idx, verbo in zip(grupos_ids, todos_rotulos):
        if idx not in grupos_semanticos:
            grupos_semanticos[idx] = []
        grupos_semanticos[idx].append(verbo)

    # ------------------------------------------------------
    # 4. DEFINIR A CHAVE DE CADA GRUPO
    #    (pode ser qualquer estratégia — aqui: o menor termo alfabético)
    # ------------------------------------------------------
    resultado = {}
    for idx, lista in grupos_semanticos.items():
        chave = sorted(lista)[0]  # chave definida por ordem alfabética
        resultado[chave] = sorted(set(lista))

    return resultado


# ------------------------------------------------------
# TESTE
# ------------------------------------------------------
if __name__ == "__main__":
    grupos = processar_csv("saida.csv")
    for k, v in grupos.items():
        print(f"{k}: {v}")
