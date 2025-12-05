from collections import defaultdict
from Levenshtein import distance as lev

def extrair_objeto(frase: str) -> str:
    """
    Retorna tudo após o verbo, ou seja, o objeto da frase.
    Ex: 'SUBSTITUIR BARRA DE DIREÇÃO' -> 'BARRA DE DIREÇÃO'
    """
    palavras = frase.split()
    if len(palavras) > 1:
        return " ".join(palavras[1:]).strip()
    return ""

def agrupar_por_objeto(grupos_por_verbo: dict, limiar=5):
    """
    Recebe um dicionário {verbo: [frases]} e retorna
    um dicionário {verbo: [grupos_de_frases]} agrupadas pelo objeto
    usando distância de Levenshtein.
    """
    resultado = defaultdict(list)

    for verbo, frases in grupos_por_verbo.items():
        grupos_objetos = []

        for frase in frases:
            objeto = extrair_objeto(frase)
            colocado = False

            # Tenta adicionar a frase em um grupo existente
            for grupo in grupos_objetos:
                objeto_centro = extrair_objeto(grupo[0])
                if lev(objeto, objeto_centro) <= limiar:
                    grupo.append(frase)
                    colocado = True
                    break

            # Se não coube em nenhum grupo, cria um novo
            if not colocado:
                grupos_objetos.append([frase])

        resultado[verbo] = grupos_objetos

    return resultado

# ----------------------
# Exemplo de uso
# ----------------------
# grupos_por_verbo já definido anteriormente
# grupos_final = agrupar_por_objeto(grupos_por_verbo)

# Para imprimir o resultado
# for verbo, grupos in grupos_final.items():
#     print(f"VERBO: {verbo}")
#     for i, g in enumerate(grupos, 1):
#         print(f"  GRUPO {i}: {g}")
#     print("-" * 50)
