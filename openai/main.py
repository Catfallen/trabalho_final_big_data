import streamlit as st
from sentence_transformers import SentenceTransformer, util
from rapidfuzz.distance import Levenshtein

# --- Modelo embeddings ---
model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Lista de verbos e frases ---
verbos = ["apertar", "limpar", "instalar", "consertar", "reparar",
          "trocar", "avaliar", "testar", "retirar", "realizar"]

# Exemplo curto, no seu caso seria 700+
frases = [
    "apertar parafuso", "aperto de parafuso",
    "consertar equipamento", "conserta equipamento",
    "trocar mangueira", "troca de mangueira",
    "limpar filtro", "limpeza do filtro"
]

# --- Gerar embeddings ---
embeddings = model.encode(frases, convert_to_tensor=True)

# --- Agrupar semanticamente ---
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

# --- Streamlit Interface ---
st.title("Revisão Manual de Agrupamento de Frases")
st.write("Cada grupo abaixo possui frases similares. Escolha a frase canônica:")

dicionario_final = {}
for idx, grupo in enumerate(grupos):
    st.write(f"**Grupo {idx+1}:**")
    escolha = st.radio("Escolha a frase canônica:", grupo, key=idx)
    for frase in grupo:
        dicionario_final[frase] = escolha

# --- Exibir resultado final ---
st.write("### Dicionário Final")
st.json(dicionario_final)
