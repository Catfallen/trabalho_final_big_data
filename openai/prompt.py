def get_prompt(grupos):
    grupos_texto = "\n".join(str(g) for g in grupos)

    prompt = f"""
Você é um sistema altamente especializado em normalização semântica de verbos e substantivos de manutenção.

Sua tarefa:
Gerar **um DICIONÁRIO UNIVERSAL** mapeando cada termo para um valor universal.

⚠️ **INSTRUÇÕES ABSOLUTAS (CUMPRA TODAS):**

1. A resposta DEVE conter **somente** um dicionário Python válido, começando com '{{' e terminando com '}}'.
   - Sem texto antes ou depois.
   - Sem explicações ou comentários.

2. Para cada grupo:
   - Agrupe pequenas variações ortográficas, flexões e erros de digitação.
   - Se houver verbos e substantivos com o mesmo significado, **sempre escolha o verbo como valor universal**.
   - Se o grupo contiver apenas substantivos **e não houver verbo equivalente**, mantenha o substantivo como valor universal.
   - Não criar palavras novas; use apenas os termos existentes.

3. Alguns termos já têm sinônimos definidos (exemplo: "substituir", "trocar", "substituição") e devem compartilhar o mesmo valor universal.
   - Por exemplo, "higienizar" e "limpar" são sinônimos: escolha um como valor universal.
   - Fazer e realizar também são sinônimos
   - "munut" significa manutenção evite a palavra manter
4. Palavras sem significado claro (“--”, “xxxx”, “pt” etc.) devem apontar para si mesmas.

Aqui estão os grupos da ETAPA 1:

{grupos_texto}

Gere **apenas** o dicionário Python final, seguindo todas as regras acima.
"""
    return prompt
