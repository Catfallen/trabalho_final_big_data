import pandas as pd
import re
from pathlib import Path
from dicionario import dicionario_universal


# --------------------------------------------------------
# Levenshtein simples
# --------------------------------------------------------
def levenshtein(a, b):
    if a == b:
        return 0

    if len(a) < len(b):
        a, b = b, a

    previous = range(len(b) + 1)
    for i, ca in enumerate(a):
        current = [i + 1]
        for j, cb in enumerate(b):
            insert = previous[j + 1] + 1
            delete = current[j] + 1
            subst = previous[j] + (ca != cb)
            current.append(min(insert, delete, subst))
        previous = current

    return previous[-1]


# --------------------------------------------------------
# separa verbo + objeto
# --------------------------------------------------------
def separar_verbo_objeto(frase):
    partes = frase.split(" ", 1)
    if len(partes) == 1:
        return partes[0].lower().strip(), ""
    return partes[0].lower().strip(), partes[1].lower().strip()


# --------------------------------------------------------
# normaliza verbo via dicionário universal
# --------------------------------------------------------
def normalizar_verbo(verbo):
    v = verbo.lower().strip()
    return dicionario_universal.get(v, v)


# --------------------------------------------------------
# Agrupa objetos por verbo usando Levenshtein
# + ORDENAÇÃO
# --------------------------------------------------------
def agrupar_objetos_por_verbo(mapeado_verbo_objetos, limiar=3):
    agrupamentos = []

    for verbo in sorted(mapeado_verbo_objetos.keys()):  # ordenar verbos
        objetos = sorted(mapeado_verbo_objetos[verbo])  # ordenar objetos antes

        grupos = []

        for obj in objetos:
            colocado = False

            for grupo in grupos:
                representante = grupo[0]
                if levenshtein(obj, representante) <= limiar:
                    grupo.append(obj)
                    grupo.sort()  # mantém cada grupo ordenado
                    colocado = True
                    break

            if not colocado:
                grupos.append([obj])

        # ordena grupos pelo primeiro elemento
        grupos.sort(key=lambda g: g[0])

        agrupamentos.append({
            "verbo": verbo,
            "objetos": grupos
        })

    return agrupamentos


# --------------------------------------------------------
# Função principal
# --------------------------------------------------------
def agrupar_frases(frases):
    lista = []

    for f in frases:
        verbo, objeto = separar_verbo_objeto(f)
        verbo_norm = normalizar_verbo(verbo)
        lista.append((verbo_norm, objeto))

    agrupado_por_verbo = {}

    for verbo, objeto in lista:
        agrupado_por_verbo.setdefault(verbo, set()).add(objeto)

    return agrupar_objetos_por_verbo({
        v: list(objs) for v, objs in agrupado_por_verbo.items()
    })


# --------------------------------------------------------
# Carrega frases únicas do CSV
# --------------------------------------------------------
def carregar_frases_unicas(CSV_PATH):
    df = pd.read_csv(CSV_PATH, sep=";")
    df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
    df = df[df["DescricaoManutencao"] != ""]
    frases_unicas = df["DescricaoManutencao"].drop_duplicates().tolist()
    return frases_unicas


# --------------------------------------------------------
if __name__ == "__main__":
    CSV_PATH = Path("saida.csv")
    frases = carregar_frases_unicas(CSV_PATH)
    grupos = agrupar_frases(frases)

    for g in grupos:
        print("\nVERBO:", g["verbo"])
        for grupo_obj in g["objetos"]:
            print("  -", grupo_obj)
