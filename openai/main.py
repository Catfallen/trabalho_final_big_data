from sentence_transformers import SentenceTransformer, util
from rapidfuzz.distance import Levenshtein

# ============================
# 1. Lista de frases
# ============================
frases = [
    "apertar parafuso", "aperto de parafuso",
    "consertar equipamento", "conserta equipamento",
    "trocar mangueira", "troca de mangueira",
    "limpar filtro", "limpeza do filtro",
    "aprert de parafuso"
]

# ============================
# 2. Extrair verbos das frases
# ============================
verbos = set()
for frase in frases:
    palavras = frase.lower().split()
    if len(palavras) == 0:
        continue
    verbo = palavras[0]
    if len(palavras) > 1 and len(palavras[1]) <= 3:
        verbo += " " + palavras[1]
    verbos.add(verbo)

verbos = list(verbos)

# ============================
# 3. Agrupar verbos semelhantes (Levenshtein)
# ============================
# Cria mapeamento: verbo_variacao -> verbo_canonico
verbo_canonico = {}
for v in verbos:
    # Se já agrupamos
    if v in verbo_canonico:
        continue
    grupo = [v]
    for o in verbos:
        if o == v or o in verbo_canonico:
            continue
        # distância relativa <= 2 considera erro de digitação
        dist = Levenshtein.distance(v, o)
        if dist <= 4:
            grupo.append(o)
    # Escolhe a forma mais “clara” (curta) como canônica
    chave = min(grupo, key=len)
    for g in grupo:
        verbo_canonico[g] = chave

print("Verbos canônicos:", verbo_canonico)

# ============================
# 4. Modelo embeddings para frases
# ============================
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(frases, convert_to_tensor=True)

# ============================
# 5. Agrupamento frases (similaridade)
# ============================
sim_matrix = util.cos_sim(embeddings, embeddings).numpy()
threshold = 0.75
visitados = set()
grupos = []

for i, frase in enumerate(frases):
    if i in visitados:
        continue
    grupo = [frase]
    visitados.add(i)
    for j in range(i+1, len(frases)):
        if sim_matrix[i][j] > threshold:
            grupo.append(frases[j])
            visitados.add(j)
    grupos.append(grupo)

# ============================
# 6. Criar dicionário universal
# ============================
dicionario = {}
for grupo in grupos:
    # pegar verbo da primeira palavra
    grupo_verbos = [f for f in grupo if verbo_canonico.get(f.split()[0], f.split()[0])]
    # chave = frase com verbo canônico mais curta
    chave = min(grupo, key=lambda x: len(x))
    for f in grupo:
        # substitui verbo pelo canônico
        palavras = f.split()
        palavras[0] = verbo_canonico.get(palavras[0], palavras[0])
        frase_corrigida = " ".join(palavras)
        dicionario[f] = chave

# ============================
# 7. Resultado
# ============================
print("\n=== DICIONÁRIO FINAL ===")
for k, v in dicionario.items():
    print(f"{k} -> {v}")
