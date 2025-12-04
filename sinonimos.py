import sys
print("STREAMLIT PYTHON:", sys.executable)


import pandas as pd
import streamlit as st
from pathlib import Path
import re
import json
import streamlit.components.v1 as components
import estado_global  # módulo para guardar variáveis globais
from sentence_transformers import SentenceTransformer
import hdbscan
import umap
import numpy as np
import pandas as pd
import re
import unidecode
from rapidfuzz.distance import Levenshtein
from nltk.stem.snowball import SnowballStemmer


def extrair_primeiras(frase):
    frase = (
        frase.lower()
        .strip()
        .replace("ã", "a")
        .replace("õ", "o")
        .replace("ç", "c")
        .encode("ascii", "ignore")
        .decode()
    )
    frase = re.sub(r"[^a-z\s]", "", frase)
    palavras = frase.split()

    if not palavras:
        return ""

    p1 = palavras[0]
    p2 = palavras[1] if len(palavras) > 1 else ""

    ## Se for "troca de", "substituicao de", "revisao de", etc.
    #if p2 in ['da','de','di','do','du']:
    
    if len(p2) < 3:
        return f"{p1} {p2}"

    return p1


# ------------------------------------------------------------
# Função para receber o dicionário vindo do JavaScript
# ------------------------------------------------------------
def receber_dict_js(dicionario):
    if isinstance(dicionario, str):
        try:
            dicionario = json.loads(dicionario)
        except:
            st.error("Erro ao converter o dicionário recebido do JavaScript.")
            return
    estado_global.DICIONARIO_UNIVERSAL = dicionario
    st.success("✅ DICIONARIO_UNIVERSAL atualizado com sucesso!")
    st.json(estado_global.DICIONARIO_UNIVERSAL)


# ------------------------------------------------------------
# Distância de Levenshtein
# ------------------------------------------------------------
def distancia_levenshtein(a, b):
    a = re.sub(r'[^a-zA-Z0-9\s]', '', a).strip().lower()
    b = re.sub(r'[^a-zA-Z0-9\s]', '', b).strip().lower()
    if len(a) == 0: return len(b)
    if len(b) == 0: return len(a)
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1): dp[i][0] = i
    for j in range(len(b) + 1): dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            custo = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+custo)
    return dp[-1][-1]


# ------------------------------------------------------------
# Função para extrair chave comparativa (segunda palavra)
# ------------------------------------------------------------
def get_key(desc):
    palavras = desc.split()
    return " ".join(palavras[1:]) if len(palavras) > 1 else desc


# ------------------------------------------------------------
# Exportar CSV
# ------------------------------------------------------------
def exportar_para_csv(grupos, max_dist):
    dados_export = []
    for idx, grupo in enumerate(grupos, 1):
        for desc, ident in grupo:
            dados_export.append({
                "Grupo": f"Grupo {idx}",
                "ID": ident,
                "Descrição": desc,
                "Distância Máxima Usada": max_dist
            })
    df_export = pd.DataFrame(dados_export)
    return df_export.to_csv(index=False).encode("utf-8")


# ------------------------------------------------------------
# MAIN STREAMLIT
# ------------------------------------------------------------
def main():
    st.title("🔤 Agrupamento Inteligente de Tarefas (765 frases)")

    caminho = Path("saida.csv")
    if not caminho.exists():
        st.error("Arquivo 'saida.csv' não encontrado.")
        return

    # ---------------------------------------------------------
    # 1. CARREGA CSV
    # ---------------------------------------------------------
    df = pd.read_csv(caminho, sep=";")
    df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
    df = df[df["DescricaoManutencao"] != ""]

    # ---------------------------------------------------------
    # 2. NORMALIZA FRASE COMPLETA
    # ---------------------------------------------------------
    def normalizar_frase(texto):
        texto = unidecode.unidecode(texto.lower())
        texto = re.sub(r"[^a-z0-9\s]", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        return texto

    frases = df["DescricaoManutencao"].apply(normalizar_frase).tolist()
    frases_unicas = sorted(set(frases))

    st.subheader("📌 Total de frases após normalização")
    st.write(f"Total: **{len(frases_unicas)}** frases únicas")

    # ---------------------------------------------------------
    # 3. EMBEDDING COM FRASE COMPLETA
    # ---------------------------------------------------------
    st.write("🔍 Gerando embeddings...")
    modelo = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
    emb = modelo.encode(frases_unicas, show_progress_bar=True)

    # ---------------------------------------------------------
    # 4. UMAP PARA REDUÇÃO DE DIMENSÃO
    # ---------------------------------------------------------
    st.write("🔧 Reduzindo dimensionalidade...")
    umap_emb = umap.UMAP(
        n_neighbors=15,
        min_dist=0.0,
        n_components=5,
        metric='cosine'
    ).fit_transform(emb)

    # ---------------------------------------------------------
    # 5. AGRUPAMENTO COM HDBSCAN
    # ---------------------------------------------------------
    st.write("📊 Agrupando frases...")
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=3,
        min_samples=1,
        metric='euclidean'
    )

    labels = clusterer.fit_predict(umap_emb)

    # ---------------------------------------------------------
    # 6. MONTA GRUPOS
    # ---------------------------------------------------------
    grupos = {}
    for frase, label in zip(frases_unicas, labels):
        grupos.setdefault(label, []).append(frase)

    # ---------------------------------------------------------
    # 7. EXIBE RESULTADO
    # ---------------------------------------------------------
    st.header("📦 Agrupamentos Encontrados")

    for label, itens in grupos.items():
        if label == -1:
            st.subheader("🟧 Grupo isolado (sem cluster)")
        else:
            st.subheader(f"🟩 Grupo {label} — {len(itens)} itens")

        st.code("\n".join(sorted(itens)))
    if df.empty:
        st.warning("Nenhuma descrição encontrada com 'trocar' ou 'substituir'.")
        return

    dados = (
        df[["DescricaoManutencao", "idtarefa"]]
        .drop_duplicates()
        .sort_values("DescricaoManutencao")
        .values.tolist()
    )

    st.info(f"📌 Total de tarefas únicas encontradas: **{len(dados)}**")

    col1, col2 = st.columns([1, 2])
    with col1:
        max_dist = st.number_input(
            "Distância máxima (Levenshtein)",
            min_value=0, max_value=20, value=2, step=1
        )
        iniciar = st.button("🔍 Iniciar agrupamento")

    if not iniciar:
        return

    placeholder = st.empty()
    progress_bar = st.progress(0)

    resultados_finais = []
    grupos_para_export = []
    visitadas = set()
    total = len(dados)

    for i in range(total):
        p1, id1 = dados[i]
        key1 = get_key(p1)
        if p1 in visitadas: continue
        visitadas.add(p1)
        grupo_atual = [(p1, id1)]
        for j in range(i + 1, total):
            p2, id2 = dados[j]
            key2 = get_key(p2)
            if p2 not in visitadas:
                dist = distancia_levenshtein(key1, key2)
                if dist <= max_dist:
                    visitadas.add(p2)
                    grupo_atual.append((p2, id2))
        if len(grupo_atual) > 1:
            grupos_para_export.append(grupo_atual)
            resultados_finais.append("---")
            for desc, ident in grupo_atual:
                resultados_finais.append(f"[{ident}] {desc}\n")
            resultados_finais.append("---")
            placeholder.markdown("\n".join(resultados_finais))
        progress_bar.progress((i + 1)/total)

    progress_bar.empty()

    if not grupos_para_export:
        st.info("Nenhum agrupamento encontrado. Tente aumentar a distância.")
        return

    st.success(f"🔎 Concluído! Foram encontrados **{len(grupos_para_export)} grupos**.")

    csv_data = exportar_para_csv(grupos_para_export, max_dist)
    st.download_button(
        label="📥 Baixar agrupamentos como CSV",
        data=csv_data,
        file_name="agrupamentos.csv",
        mime="text/csv"
    )

    # -------------------------------------------------
    # INTERFACE JAVASCRIPT
    # -------------------------------------------------
    grupos_json = json.dumps(grupos_para_export, ensure_ascii=False)

    html = f"""
<script>
const grupos = {grupos_json};

function montarUI() {{
    let html = "<h3 style='color:white'>Dicionário Universal</h3>";

    grupos.forEach((grupo, idx) => {{
        html += `<div style='border:1px solid white;color:white;padding:10px;margin:10px;border-radius:6px;'>
                    <b>Grupo ${{idx+1}}</b><br><br>`;
        grupo.forEach(item => {{
            html += `<label>
                        <input type='checkbox' class='chk' data-grupo='g${{idx}}' value='${{item[0]}}'>
                        ${{item[0]}}
                     </label><br>`;
        }});
        html += "</div>";
    }});

    html += "<button onclick='gerarDict()' style='padding:10px 20px;margin-top:10px;'>Gerar Dicionário</button>";
    html += "<pre id='resultado' style='margin-top:20px;background:#222;color:#0f0;padding:10px;'></pre>";
    document.getElementById("app").innerHTML = html;
}}

function gerarDict() {{
    const dict = {{}};
    const gruposUnicos = new Set();
    document.querySelectorAll(".chk").forEach(ch => gruposUnicos.add(ch.dataset.grupo));

    gruposUnicos.forEach(grp => {{
        const checkboxes = document.querySelectorAll(`.chk[data-grupo='${{grp}}']`);
        let principal = null;
        for (let ch of checkboxes) {{
            if (ch.checked) {{
                principal = ch.value; break;
            }}
        }}
        if (principal) {{
            checkboxes.forEach(ch => {{
                if (ch.checked) dict[ch.value] = principal;
            }});
        }}
    }});

    document.getElementById("resultado").innerText = JSON.stringify(dict, null, 4);
    sessionStorage.setItem("dicionario_universal", JSON.stringify(dict));

    // Envia para a API /enviar
    fetch("http://localhost:3000/enviar", {{
        method: "POST",
        headers: {{
            "Content-Type": "application/json"
        }},
        body: JSON.stringify({{ dict: dict }})
    }})
    .then(response => response.json())
    .then(data => {{
        console.log("Resposta da API:", data);
        alert("Dicionário enviado com sucesso para a API!");
    }})
    .catch(err => {{
        console.error("Erro ao enviar o dict:", err);
        alert("Falha ao enviar o dicionário para a API.");
    }});
}}

document.addEventListener("DOMContentLoaded", montarUI);
</script>

<div id="app"></div>
"""
    components.html(html, height=700, scrolling=True)

    # ------------------------------------------------------------
    # LEITURA DO DICT GERADO PELO JAVASCRIPT
    # ------------------------------------------------------------
    dict_js = st.text_input("Dicionário recebido do navegador (sessionStorage):")
    if dict_js:
        receber_dict_js(dict_js)


if __name__ == "__main__":
    main()
