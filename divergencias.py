import pandas as pd
import streamlit as st
from pathlib import Path
import re
import json
import streamlit.components.v1 as components

# ------------------------------------------------------------
# Distância de Levenshtein (implementação pura, com limpeza)
# ------------------------------------------------------------
def distancia_levenshtein(a, b):
    a = re.sub(r'[^a-zA-Z0-9\s]', '', a).strip().lower()
    b = re.sub(r'[^a-zA-Z0-9\s]', '', b).strip().lower()

    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            custo = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + custo
            )

    return dp[-1][-1]

# ------------------------------------------------------------
# Função para exportar resultados para CSV
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
    return df_export.to_csv(index=False).encode('utf-8')

# ------------------------------------------------------------
# STREAMLIT PRINCIPAL
# ------------------------------------------------------------
def main():
    st.set_page_config(page_title="Agrupamento Inteligente", layout="wide")
    st.title("🔤 Agrupamento de Palavras (Janela dinâmica por inicial)")

    caminho = Path("saida.csv")
    if not caminho.exists():
        st.error("Arquivo 'saida.csv' não encontrado. Certifique-se de que ele está no diretório correto.")
        return

    df = pd.read_csv(caminho, sep=";")
    df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
    df["idtarefa"] = df["idtarefa"].astype(str).str.strip()
    df = df[df["DescricaoManutencao"] != ""]

    dados = (
        df[["DescricaoManutencao", "idtarefa"]]
        .drop_duplicates()
        .sort_values("DescricaoManutencao")
        .values.tolist()
    )

    new_dados = []

    for x in dados:
        if 'trocar' in str(x).lower():
            continue
        if 'substituir' in str(x).lower():
            continue
        else:
            new_dados.append(x)

    st.info(f"📌 Total de tarefas únicas encontradas: **{len(new_dados)}**")

    col1, col2 = st.columns([1, 2])
    with col1:
        max_dist = st.number_input(
            "Distância máxima (Levenshtein)",
            min_value=0,
            max_value=20,
            value=2,
            step=1
        )
        iniciar = st.button("🔍 Iniciar agrupamento")

    if iniciar:
        placeholder = st.empty()
        progress_bar = st.progress(0)

        resultados_finais = []
        grupos_para_export = []
        visitadas = set()
        total = len(dados)

        for i in range(total):
            p1, id1 = dados[i]
            if p1 in visitadas:
                continue
            visitadas.add(p1)
            grupo_atual = [(p1, id1)]
            inicial = p1[0].lower()

            j = i + 1
            while j < total:
                p2, id2 = dados[j]
                if p2[0].lower() != inicial:
                    break
                if p2 not in visitadas:
                    dist = distancia_levenshtein(p1, p2)
                    if dist <= max_dist:
                        visitadas.add(p2)
                        grupo_atual.append((p2, id2))
                j += 1

            if len(grupo_atual) > 1:
                grupos_para_export.append(grupo_atual)
                resultados_finais.append("---")
                for desc, ident in grupo_atual:
                    resultados_finais.append(f"[{ident}] {desc}\n")
                resultados_finais.append("---")
                placeholder.markdown("\n".join(resultados_finais))

            progress_bar.progress((i + 1) / total)

        progress_bar.empty()

        if grupos_para_export:
            total_grupos = len(grupos_para_export)
            total_elementos = sum(len(g) for g in grupos_para_export)

            st.success(
                f"🔎 Agrupamento concluído!\n\n"
                f"🧩 **Grupos encontrados:** {total_grupos}\n"
                f"📌 **Total de elementos agrupados:** {total_elementos}\n"
                f"📄 **Tarefas únicas analisadas:** {len(dados)}"
            )

            csv_data = exportar_para_csv(grupos_para_export, max_dist)
            st.download_button(
                label="📥 Baixar agrupamentos como CSV",
                data=csv_data,
                file_name="agrupamentos.csv",
                mime="text/csv"
            )

            # --------------------------
            # Bloco JS interativo
            # --------------------------
            grupos_json = json.dumps(grupos_para_export, ensure_ascii=False)

            js_code = f"""
<script>
const grupos = {grupos_json};

function montarUI() {{
    let html = "<h3 style='color:white;'>Dicionário Universal</h3>";

    grupos.forEach((grupo, idx) => {{
        html += `<div style='border:1px solid white;color:white;padding:10px;margin:10px;border-radius:6px;'>
            <b>Grupo ${{idx + 1}}</b><br><br>`;

        grupo.forEach(item => {{
            const desc = item[0];
            html += `
                <label>
                    <input type='checkbox' class='chk' data-grupo="${{idx}}" value="${{desc}}">
                    ${{desc}}
                </label><br>`;
        }});

        html += "</div>";
    }});

    html += "<button onclick='gerarDict()' style='padding:10px 20px;'>Gerar Dicionário</button>";
    html += "<pre id='resultado' style='margin-top:20px;background:#222;color:#0f0;padding:10px;'></pre>";

    document.getElementById("app").innerHTML = html;
}}

async function gerarDict() {{

    const checks = document.querySelectorAll(".chk");
    let gruposSelecionados = {{}};
    let dict = {{}};

    checks.forEach(ch => {{
        if (ch.checked) {{
            const g = ch.dataset.grupo;
            if (!gruposSelecionados[g]) gruposSelecionados[g] = [];
            gruposSelecionados[g].push(ch.value);
        }}
    }});

    Object.values(gruposSelecionados).forEach(items => {{
        if (items.length === 0) return;

        const universal = items[0];

        items.forEach(item => {{
            dict[item] = universal;
        }});
    }});

    document.getElementById("resultado").innerText = JSON.stringify(dict, null, 4);

    // ENVIO CORRIGIDO  ✔✔✔
    try {{
        const resposta = await fetch("http://localhost:3000/palavras", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ dict }})
        }});

        if (!resposta.ok) {{
            throw new Error("Falha ao enviar dicionário");
        }}

        console.log("Enviado com sucesso");
    }} catch(err) {{
        console.error("Erro ao enviar:", err);
    }}
}}

document.addEventListener("DOMContentLoaded", montarUI);
</script>

<div id="app"></div>
"""

            components.html(js_code, height=600, scrolling=True)

        else:
            st.info("Nenhum agrupamento encontrado com os critérios atuais. Tente aumentar a distância máxima.")

if __name__ == "__main__":
    main()
