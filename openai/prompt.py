def get_prompt(grupos):
    grupos_texto = "\n".join(str(g) for g in grupos)

    prompt = f"""
Você é um sistema especialista em normalização semântica de termos de manutenção.

Regras obrigatórias:

1. Agrupe todos os termos que têm o mesmo significado, incluindo verbos e substantivos.
   - Ex: "substituir", "substituição", "trocar", "troca" → valor universal "substituir"
   - Ex: "manutenção", "manutencao", "manter" → valor universal "manutenção"

2. Corrija apenas erros ortográficos ou pequenas variações dentro de cada termo.
   - Ex: "subistituir" → "substituir"

3. Palavras sem significado claro ou códigos devem apontar para si mesmas.
   - Ex: "--" → "--", "xxxxx" → "xxxxx"

4. A resposta DEVE ser somente um dicionário Python válido.
   - Sem texto adicional, sem explicações, sem comentários.

Aqui estão os grupos da ETAPA 1:

{grupos_texto}

Gere EXCLUSIVAMENTE o dicionário Python final.
"""
    return prompt
