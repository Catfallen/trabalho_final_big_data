from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

# Lista de verbos extraídos das frases (primeira e segunda palavra curta)
verbos = ['apertar', 'aperto de', 'consertar', 'conserta', 
          'trocar', 'troca de', 'limpar', 'limpeza do', 'aprert de']

# ============================
# 1. Normalizar verbos (fuzzy match)
# ============================
normalizados = {}
for v in verbos:
    # checa se v é parecido com algum verbo já normalizado
    achou = False
    for k in normalizados.keys():
        if fuzz.ratio(v, k) >= 80:  # ajuste threshold
            normalizados[v] = k
            achou = True
            break
    if not achou:
        normalizados[v] = v

# ============================
# 2. Agrupar palavras semelhantes
# ============================
grupos = {}
for orig, canon in normalizados.items():
    grupos.setdefault(canon, []).append(orig)

# ============================
# 3. Resultado
# ============================
print("\n=== GRUPOS DE VERBOS ===")
for k, v in grupos.items():
    print(f"{k}: {v}")
