from sentence_transformers import SentenceTransformer, util

# Modelo leve para CPU
model = SentenceTransformer("all-MiniLM-L6-v2")

# Lista de verbos iniciais
verbos = [
    "apertar", "limpar", "instalar", "consertar", "reparar",
    "trocar", "avaliar", "testar", "retirar", "realizar"
]

# Lista de frases
frases = [
    "apertar parafuso",
    "aperto de parafuso",
    "consertar equipamento",
    "conserta equipamento",
    "trocar mangueira",
    "troca de mangueira",
    "limpar filtro",
    "limpeza do filtro"
]

# Gerar embeddings
embeddings = model.encode(frases, convert_to_tensor=True)

# Similaridade coseno
sim_matrix = util.cos_sim(embeddings, embeddings).numpy()
threshold = 0.75  # ajustar se quiser mais ou menos agrupamento

# Agrupamento e escolha da frase canônica
dicionario = {}
visitados = set()

for i, frase in enumerate(frases):
    if i in visitados:
        continue
    
    grupo = [frase]
    visitados.add(i)
    
    for j in range(i+1, len(frases)):
        if sim_matrix[i][j] > threshold:
            grupo.append(frases[j])
            visitados.add(j)
    
    # Escolher a frase **com verbo correto e mais “clara”** como chave canônica
    chave = min([f for f in grupo if f.split()[0] in verbos], key=len)
    
    for f in grupo:
        dicionario[f] = chave

# Resultado
print("=== DICIONÁRIO FINAL ===")
for k, v in dicionario.items():
    print(f"{k} -> {v}")
