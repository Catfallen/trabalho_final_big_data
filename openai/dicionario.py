import json

dicionario_universal = {}

with open("dicionario.json", "r", encoding="utf-8") as arquivo:
    dicionario_universal = json.load(arquivo)

print(dicionario_universal)
