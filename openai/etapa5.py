from time import sleep
from conn import manus_get, manus_post

def criar_prompt_universal(grupos_refinados):
    """
    Cria o prompt para Manus a partir de grupos refinados.
    Cada chave é apenas um contexto (nome do grupo), e cada lista interna contém frases.
    """
    prompt_dict = {}
    for verbo, grupos in grupos_refinados.items():
        for i, grupo in enumerate(grupos, start=1):
            chave = f"{verbo}_{i}"  # apenas contexto
            prompt_dict[chave] = grupo

    prompt_texto = f"""
Você receberá um dicionário com chaves representando grupos e valores que são listas de frases.
Sua tarefa é criar um 'valor universal' para cada frase, seguindo estas regras:

1. O nome da chave do grupo é apenas contexto. **Não unifique frases baseado nele**.
2. Frases devem receber o mesmo valor universal **somente se representam a mesma ação sobre o mesmo objeto**.
3. Corrija pequenas falhas de digitação, mas use **o termo oficial do sistema**.
   Por exemplo, "ESGUINCHO" e "ESGUICHO" podem ser unificados, mas usando o termo correto existente.
4. Frases que descrevem objetos ou ações diferentes devem permanecer separadas.
5. Se dentro de um grupo não houver nada em comum, cada frase deve receber seu próprio valor universal individual.
6. Retorne um JSON no formato: {{ "frase_original": "valor_universal" }}

Exemplo:
{{
    "COMPLETAR GÁS": "COMPLETAR GÁS",
    "COMPLETAR ÓLEO": "COMPLETAR ÓLEO",
    "CONSERTAR ESGUICHO": "CONSERTAR ESGUICHO",
    "CONSERTAR ESGUINCHO": "CONSERTAR ESGUICHO"
}}

Agora, processe o seguinte dicionário:
{prompt_dict}
"""
    return prompt_texto

def dicionario_final(grupos_refinados):
    prompt = criar_prompt_universal(grupos_refinados)
    
    # Envia para o Manus
    resposta_post = manus_post(prompt)
    task_id = resposta_post.get('task_id')
    
    # Aguarda até a tarefa ser concluída
    while True:
        sleep(2)
        result = manus_get(task_id)
        status = result.get("status")
        if status == "completed":
            break
        print("Ainda processando... aguardando 2s")
    
    # Resultado final
    json_final = result.get("result")  # assumindo que o Manus retorna o JSON aqui
    print("JSON COMPLETO:", json_final)
    return json_final

# ------------------------------
# Exemplo de uso
# ------------------------------
# grupos_final já contém os grupos refinados por verbo e objeto
# resultado = dicionario_final(grupos_final)
