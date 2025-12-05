import pandas as pd
from pathlib import Path
import re
from Levenshtein import distance as lev

# ------------------------------------------------------
# Funções auxiliares
# ------------------------------------------------------

PREPOSICOES = {"de", "da", "do", "das", "dos", "a", "o", "na", "no"}




def normalizar_verbo(texto: str) -> str:
    """
    Normaliza o verbo:
    - minúsculas
    - remove preposições depois do verbo
    - remove plurais simples
    - mantém substantivos derivados para agrupar depois via Levenshtein
    """
    texto = texto.lower().strip()
    palavras = texto.split()

    if not palavras:
        return texto

    verbo = palavras[0]

    # Se segunda palavra for preposição → ignora
    if len(palavras) > 1 and palavras[1] in PREPOSICOES:
        return f"{verbo}"

    return verbo


def agrupar_levenshtein(palavras, max_dist=5):
    """
    Agrupa palavras semelhantes pela distância de Levenshtein.
    """
    grupos = []
    usadas = set()

    for palavra in palavras:
        if palavra in usadas:
            continue

        grupo = [palavra]
        usadas.add(palavra)

        for outra in palavras:
            if outra in usadas:
                continue
            if palavra[0] != outra[0]:
                continue  # somente mesma letra inicial

            if lev(palavra, outra) <= max_dist:
                grupo.append(outra)
                usadas.add(outra)

        grupos.append(grupo)

    return grupos


# ------------------------------------------------------
# CARREGA CSV E EXTRAI VERBOS
# ------------------------------------------------------

caminho = Path("saida.csv")
df = pd.read_csv(caminho, sep=";")

df["DescricaoManutencao"] = (
    df["DescricaoManutencao"]
    .astype(str)
    .str.strip()
)

df = df[df["DescricaoManutencao"] != ""]

# Extrai verbo inicial normalizado
verbos = set()

for descricao in df["DescricaoManutencao"]:
    palavras = descricao.lower().split()
    if not palavras:
        continue

    verbo = normalizar_verbo(descricao)
    verbos.add(verbo)

verbos = list(sorted(verbos))

# ------------------------------------------------------
# AGRUPAMENTO ETAPA 1
# ------------------------------------------------------

grupos = agrupar_levenshtein(verbos)

# ------------------------------------------------------
# EXIBE RESULTADO
# ------------------------------------------------------

print("\n===== GRUPOS DA ETAPA 1 =====\n")
for g in grupos:
    print(g)

print("\nTotal de verbos antes:", len(verbos))
print("Total de grupos depois:", len(grupos))