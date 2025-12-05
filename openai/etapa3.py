import pandas as pd
from collections import defaultdict
from dicionario import dicionario_universal
from etapa4 import agrupar_por_objeto,segunda_rodada_levenshtein
from etapa5 import dicionario_final
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

#for verbo, frases in grupos_por_verbo.items():
#    print("VERBO NORMALIZADO:", verbo)
#    print("FRASES DO GRUPO:", frases)
#    print("-" * 40)
    
    
print("Iniciando etapa 4")

grupos_final = agrupar_por_objeto(grupos_por_verbo)

grupos_refinados = segunda_rodada_levenshtein(grupos_final, limiar=4, tamanho_max=10)



# Impressão resumida
for verbo, grupos in grupos_refinados.items():
    print(f"VERBO: {verbo}")
    for i, g in enumerate(grupos, 1):
        print(f"  GRUPO {i} ({len(g)} itens): {g}")
    print("-"*50)
    

print(grupos_refinados)

json_final = dicionario_final(grupos_refinados)

#segunda rodada do levenshtein

#grupos_pares = #filtro do grupos_final 2 ou mais elementos
# Para imprimir o resultado
#for verbo, grupos in grupos_final.items():
#    print(f"VERBO: {verbo}")
#    for i, g in enumerate(grupos, 1):
#        print(f"  GRUPO {i}: {g}")
#    print("-" * 50)


# Mantém apenas grupos com 2 ou mais elementos
#grupos_pares = [grupo for grupo in grupos_final if len(grupo) >= 2]

# Impressão dos grupos filtrados
#for i, grupo in enumerate(grupos_pares, 1):
#    print(f"GRUPO {i}: {grupo}")
