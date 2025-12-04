from sentence_transformers import SentenceTransformer
import hdbscan
import umap
import numpy as np
import pandas as pd
import re
import unidecode
from rapidfuzz.distance import Levenshtein
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer("portuguese")

verbos = [
    "abastecer",
    "aguardando",
    "ajustar",
    "alinhar",
    "apertar",
    "aperto de",
    "aplicacao de",
    "aplicar",
    "arquente",
    "avaliar",
    "avaliar do",
    "cacamba",
    "calibrar",
    "calibrar ",
    "colar",
    "colocar",
    "completar",
    "completar ",
    "completar gs",
    "confeccionar",
    "conferir",
    "conserta",
    "consertar",
    "conserto de",
    "consetar de",
    "corrigir",
    "corrigir ",
    "desempenar",
    "desempeno da",
    "desengrenar",
    "desobstruir",
    "drenar ",
    "equipamento",
    "extracao de",
    "falha",
    "fazer",
    "fixacao da",
    "fixar",
    "higienizar",
    "inspecionar",
    "instalacao",
    "instalacao de",
    "instalar",
    "limpar",
    "limpeza da",
    "limpeza de",
    "limpeza no",
    "lubrificacao",
    "lubrificacao ",
    "mangueira",
    "manut",
    "manutencao",
    "manutencao no",
    "preparacao",
    "preparar",
    "pt",
    "realizar",
    "reaperta",
    "reapertar",
    "reaproveitamento de",
    "rebitar",
    "recarga",
    "recolher",
    "recondicionamento de",
    "recondicionar",
    "reconectar",
    "recuperar",
    "reforcar",
    "reforma",
    "regulagem do",
    "regular",
    "reparar",
    "reparo do",
    "reparo no",
    "reposicao",
    "retira",
    "retirar",
    "revisao",
    "revisar",
    "revisar os",
    "sanar",
    "servico",
    "servico de",
    "soldar",
    "soldar ",
    "soldar o",
    "subistituir",
    "substituicao",
    "substituicao de",
    "substituicao do",
    "substituir",
    "substitur",
    "t a",
    "tensionar",
    "testar",
    "tirar",
    "trava de",
    "troca",
    "troca da",
    "troca de",
    "troca do",
    "trocar",
    "trocar ",
    "vericar",
    "verificar",
    "verificar ar",
    "vulcanizacao de",
    "xxxxx ",
    "xxxxxx ",
    "xxxxxxx ",
    "xxxxxxxx ",
    "xxxxxxxxx ",
    "xxxxxxxxxxxxxx "
]


def normalizar(p):
    p = unidecode.unidecode(p.lower())
    p = re.sub(r"[^a-z\s]", " ", p)
    p = re.sub(r"\s+", " ", p).strip()

    # pega só a primeira palavra
    tokens = p.split()
    if tokens:
        p = tokens[0]
    return p

def simil(p1, p2):
    d = Levenshtein.normalized_distance(p1, p2)  # 0 = igual
    return 1 - d

# ---------------------------------------------------------
# 1. NORMALIZAÇÃO
# ---------------------------------------------------------
verbos_norm = [normalizar(v) for v in verbos]
verbos_norm = [v for v in verbos_norm if v.strip()]

# ---------------------------------------------------------
# 2. EMBEDDINGS (modelo melhor)
# ---------------------------------------------------------
modelo = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
emb = modelo.encode(verbos_norm)

# ---------------------------------------------------------
# 3. REDUÇÃO DE RUÍDO (UMAP)
# ---------------------------------------------------------
umap_emb = umap.UMAP(
    n_neighbors=15,
    min_dist=0.0,
    n_components=5,
    metric='cosine'
).fit_transform(emb)

# ---------------------------------------------------------
# 4. CLUSTERING AUTOMÁTICO (HDBSCAN)
# ---------------------------------------------------------
clusterer = hdbscan.HDBSCAN(
    min_cluster_size=2,
    min_samples=1,
    metric='euclidean'
)

labels = clusterer.fit_predict(umap_emb)

# ---------------------------------------------------------
# 5. PÓS-PROCESSAMENTO (une equivalências morfológicas e grafia)
# ---------------------------------------------------------
clusters = {}

for verbo, label in zip(verbos_norm, labels):
    if label == -1:
        # tentar achar cluster próximo
        inserted = False
        for g in clusters:
            if not isinstance(g, str):
                continue  # ignora clusters numericos
            if simil(verbo, g) > 0.80 or stemmer.stem(verbo) == stemmer.stem(g):
                clusters[g].append(verbo)
                inserted = True
                break
        if not inserted:
            clusters[verbo] = [verbo]
    else:
        clusters.setdefault(label, []).append(verbo)

# ---------------------------------------------------------
# 6. EXIBIR RESULTADO
# ---------------------------------------------------------
for grupo, itens in clusters.items():
    print("\n--- Grupo ---")
    print("\n".join(sorted(set(itens))))
