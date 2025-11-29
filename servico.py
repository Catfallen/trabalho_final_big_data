import pandas as pd
import streamlit as st
from pathlib import Path
import re
import json

# ------------------------------------------------------------
# FUNÇÕES DE CARREGAMENTO DE DADOS
# ------------------------------------------------------------
def carregar_json_local(caminho):
    """Carrega um JSON local de forma segura."""
    caminho = Path(caminho)
    if not caminho.exists():
        return {}

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao ler {caminho}: {e}")
        return {}

def carregar_json_upper(caminho):
    """Carrega JSON e converte todas as chaves para UPPERCASE."""
    caminho = Path(caminho)
    if not caminho.exists():
        return {}

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {k.upper(): v for k, v in data.items()}
    except Exception as e:
        st.error(f"Erro ao ler {caminho}: {e}")
        return {}

# ------------------------------------------------------------
# FUNÇÃO DE NORMALIZAÇÃO DE DESCRIÇÕES
# ------------------------------------------------------------
def normalizar_descricao(texto, sinonimos, universal):
    """
    Normaliza a descrição aplicando dicionário universal e sinônimos.
    """
    if not isinstance(texto, str) or texto.strip() == "":
        return texto

    original = texto.strip()
    t_upper = original.upper()

    # 1) Verifica correspondência exata no dicionário universal
    if t_upper in universal:
        return universal[t_upper]

    # 2) Aplica sinônimos
    texto_lower = original.lower()
    for palavra, base in sinonimos.items():
        texto_lower = re.sub(rf"\b{re.escape(palavra.lower())}\b", base.lower(), texto_lower)

    # 3) Verifica novamente após aplicar sinônimos
    if texto_lower.upper() in universal:
        return universal[texto_lower.upper()]

    # 4) Retorna versão limpa
    return texto_lower

# ------------------------------------------------------------
# STREAMLIT PRINCIPAL
# ------------------------------------------------------------
def main():
    st.set_page_config(page_title="Normalização de Tarefas", layout="wide")

    # ------------------------------
    # Carregar dicionários
    # ------------------------------
    sinonimos = carregar_json_local("dicionarios/dict_sinonimo.json")
    universal = carregar_json_upper("dicionarios/dict.json")

    # ------------------------------
    # Carregar CSV
    # ------------------------------
    caminho = Path("saida.csv")
    arquivo = st.file_uploader("Enviar CSV", type=["csv"])
    if arquivo:
        df = pd.read_csv(arquivo, sep=";")
    elif caminho.exists():
        df = pd.read_csv(caminho, sep=";")
    else:
        st.error("Nenhum CSV encontrado.")
        st.stop()

    # ------------------------------
    # Normalizar descrições
    # ------------------------------
    df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str)
    df["DescricaoNormalizada"] = df["DescricaoManutencao"].apply(
        lambda x: normalizar_descricao(x, sinonimos, universal)
    )

    # ------------------------------
    # Tarefas únicas + contagem ORIGINAL
    # ------------------------------
    st.subheader("🧾 Tarefas Únicas + Contagem Original")
    df_contagem_original = (
        df.groupby(["DescricaoManutencao", "DescricaoNormalizada"])
        .size()
        .reset_index(name="QuantidadeOriginal")
        .sort_values(by="QuantidadeOriginal", ascending=False)
    )
    st.dataframe(df_contagem_original, use_container_width=True)

    # ------------------------------
    # Contagem FINAL normalizada
    # ------------------------------
    st.subheader("🏆 Ranking de Tarefas (Normalizadas)")
    contagem_final = (
        df["DescricaoNormalizada"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "Tarefa Normalizada", "DescricaoNormalizada": "Quantidade"})
    )
    contagem_final.columns = ["Tarefa Normalizada", "Quantidade"]
    st.dataframe(contagem_final, use_container_width=True)


if __name__ == "__main__":
    main()
