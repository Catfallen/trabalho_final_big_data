import pandas as pd
from collections import defaultdict
from dicionario import dicionario_universal
from etapa4 import agrupar_por_objeto
CSV_PATH = "saida.csv"

# ---------------------------
# Função auxiliar
# ---------------------------

def normalizar_verbo(frase: str):
    """Extrai e normaliza o verbo inicial da frase usando o dicionário universal"""
    frase = frase.lower().strip()
    palavras = frase.split()
    if not palavras:
        return ""
    verbo = palavras[0]
    verbo_normalizado = dicionario_universal.get(verbo, verbo)
    return verbo_normalizado

# ---------------------------
# Carrega CSV e frases únicas
# ---------------------------

df = pd.read_csv(CSV_PATH, sep=";")
df["DescricaoManutencao"] = df["DescricaoManutencao"].astype(str).str.strip()
df = df[df["DescricaoManutencao"] != ""]

frases_unicas = df["DescricaoManutencao"].drop_duplicates().tolist()
frases_unicas = sorted(frases_unicas)

# ---------------------------
# Agrupamento apenas pelo verbo normalizado
# ---------------------------

grupos_por_verbo = defaultdict(list)

for frase in frases_unicas:
    verbo = normalizar_verbo(frase)
    if verbo:
        grupos_por_verbo[verbo].append(frase)

# ---------------------------
# Exibe resultados
# ---------------------------

for verbo, frases in grupos_por_verbo.items():
    print("VERBO NORMALIZADO:", verbo)
    print("FRASES DO GRUPO:", frases)
    print("-" * 40)
    
    
print("Iniciando etapa 4")

grupos_final = agrupar_por_objeto(grupos_por_verbo)

# Para imprimir o resultado
for verbo, grupos in grupos_final.items():
    print(f"VERBO: {verbo}")
    for i, g in enumerate(grupos, 1):
        print(f"  GRUPO {i}: {g}")
    print("-" * 50)