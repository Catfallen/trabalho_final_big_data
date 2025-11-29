const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const caminho = path.join(__dirname, "..","dicionarios","dict_sinonimo.json"); // Caminho do arquivo JSON
const caminho_sinonimo = path.join(__dirname,"..",'dicionarios',"dict.json"); //caminho do sinonimo
let DICIONARIO_UNIVERSAL = {};

// Carrega o dict do arquivo, se existir
if (fs.existsSync(caminho)) {
    try {
        const dados = fs.readFileSync(caminho, "utf-8");
        DICIONARIO_UNIVERSAL = JSON.parse(dados);
        console.log("Dicionário carregado do arquivo.");
    } catch (err) {
        console.error("Erro ao carregar o dict do arquivo:", err);
    }
}

// Rota POST para receber o dicionário
app.post("/enviar", async (req, res) => {
    const { dict } = req.body;
    if (!dict || typeof dict !== "object") {
        return res.status(400).json({ error: "Dict inválido ou ausente." });
    }
    DICIONARIO_UNIVERSAL = dict;

    // Salva no arquivo
    try {
        fs.writeFileSync(caminho, JSON.stringify(DICIONARIO_UNIVERSAL, null, 4), "utf-8");
        console.log("Dicionário salvo no arquivo.");
    } catch (err) {
        console.error("Erro ao salvar dict:", err);
        return res.status(500).json({ error: "Falha ao salvar o dict no arquivo." });
    }

    res.json({ message: "Dicionário recebido e salvo com sucesso!", dict: DICIONARIO_UNIVERSAL });
});

app.post("/palavras",async (req,res)=>{
    const { dict } = req.body;
    if (!dict || typeof dict !== "object") {
        return res.status(400).json({ error: "Dict inválido ou ausente." });
    }
    let sinonimos = dict;

    // Salva no arquivo
    try {
        fs.writeFileSync(caminho_sinonimo, JSON.stringify(sinonimos, null, 4), "utf-8");
        console.log("Dicionário salvo no arquivo.");
    } catch (err) {
        console.error("Erro ao salvar dict:", err);
        return res.status(500).json({ error: "Falha ao salvar o dict no arquivo." });
    }

    res.json({ message: "Dicionário recebido e salvo com sucesso!", dict: sinonimos });
})


// Rota GET para recuperar o dicionário
app.get("/get", async (req, res) => {
    res.json({ dict: DICIONARIO_UNIVERSAL });
});

app.listen(3000, () => {
    console.log("API rodando em http://localhost:3000");
});
