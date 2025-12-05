import pandas as pd
import streamlit as st
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz

# ======================================================
# STREAMLIT
# ======================================================
st.title("🔤 Agrupamento de Verbos - Correção de Erros")

caminho = Path("saida.csv")
if not caminho.exists():
    st.error("Arquivo 'saida.csv' não encontrado.")
    st.stop()

# ------------------------------------------------------
# 1. CARREGA CSV
# ------------------------------------------------------
df = pd.read_csv(caminho, sep=";")
df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
df = df[df["DescricaoManutencao"] != ""]

# ------------------------------------------------------
# 2. EXTRAI VERBOS
# ------------------------------------------------------
verbos = set()
for descricao in df["DescricaoManutencao"]:
    palavras = descricao.lower().split()
    if len(palavras) == 0:
        continue
    verbo = palavras[0]
    if len(palavras) > 1 and len(palavras[1]) <= 3:
        verbo += " " + palavras[1]
    verbos.add(verbo)

verbos = list(verbos)
st.write(f"Total de verbos únicos: {len(verbos)}")
for v in verbos:
    st.write(f"{v}")
# ------------------------------------------------------
# 3. NORMALIZA VERBOS COM ERROS DE DIGITAÇÃO
# ------------------------------------------------------
normalizados = {}
for v in verbos:
    achou = False
    for k in normalizados.keys():
        if fuzz.ratio(v, k) >= 80:  # threshold pode ser ajustado
            normalizados[v] = k
            achou = True
            break
    if not achou:
        normalizados[v] = v

# ------------------------------------------------------
# 4. AGRUPA POR CHAVE
# ------------------------------------------------------
grupos = {}
for orig, canon in normalizados.items():
    grupos.setdefault(canon, []).append(orig)

# ------------------------------------------------------
# 5. MOSTRA RESULTADO
# ------------------------------------------------------
st.write("=== GRUPOS DE VERBOS ===")
for k, v in grupos.items():
    st.write(f"{k}: {v}")

# ------------------------------------------------------
# 6. (OPCIONAL) SALVAR EM JSON
# ------------------------------------------------------
import json
with open("grupos_verbos.json", "w", encoding="utf-8") as f:
    json.dump(grupos, f, ensure_ascii=False, indent=4)
st.success("Grupos de verbos salvos em 'grupos_verbos.json'")
