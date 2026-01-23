import { BedrockAgentRuntimeClient, InvokeAgentCommand } from "@aws-sdk/client-bedrock-agent-runtime";
import { BedrockRuntimeClient, ConverseCommand } from "@aws-sdk/client-bedrock-runtime";
import { fromIni } from "@aws-sdk/credential-providers";
import dotenv from "dotenv";

dotenv.config();

const credentials = fromIni({ profile: process.env.AWS_PROFILE });
const REGION = process.env.AWS_REGION;

// CONNEXIÓ 1: Model directe (per a extracció de JSON)
const directClient = new BedrockRuntimeClient({ region: REGION, credentials });

// CONNEXIÓ 2: Agent (per a consultes RAG / Normativa)
const agentClient = new BedrockAgentRuntimeClient({ region: REGION, credentials });

const SYSTEM_PROMPT_EXTRACTOR = `Ets un extractor de paràmetres de FP. 
Respon EXCLUSIVAMENT amb JSON pur. 
Camps: nom_cicle, familia, provincia, comarca, localitat, grau (BÁSICO, MEDIO, SUPERIOR, CE MEDIO, CE SUPERIOR).
Exemple: {"tasca": "PARAMETRITZAR", "params": {"nom_cicle": "DAW", "localitat": "Gandia"}}`;

export const interpretarPregunta = async (missatgeUsuari, sessionId = "sessio-temporal") => {
    try {
        // 1. DECIDIR QUINA CONNEXIÓ UTILITZAR
        // Una forma senzilla és mirar si la pregunta conté paraules clau de "normativa/acadèmiques"
        const esConsultaAcademica = /mòdul|assignatura|hora|requisit|accés|normativa|durada|puc entrar/i.test(missatgeUsuari);

        if (esConsultaAcademica) {
            console.log("--- Utilitzant CONNEXIÓ 2: Agent (RAG) ---");
            return await cridarAgent(missatgeUsuari, sessionId);
        } else {
            console.log("--- Utilitzant CONNEXIÓ 1: Model Directe (JSON) ---");
            return await cridarModelDirecte(missatgeUsuari);
        }

    } catch (error) {
        console.error("Error en interpretarPregunta:", error);
        throw error;
    }
};

// Funció per a la Connexió 1 (Model Directe)
async function cridarModelDirecte(text) {
    const command = new ConverseCommand({
        modelId: process.env.AWS_MODEL_ID,
        messages: [{ role: "user", content: [{ text: SYSTEM_PROMPT_EXTRACTOR + "\n\nPregunta: " + text }] }],
        inferenceConfig: { temperature: 0.1, maxTokens: 500 }
    });

    const response = await directClient.send(command);
    const resultText = response.output.message.content[0].text.trim();
    
    return {
        tipus: "BASE_DE_DADES",
        params: JSON.parse(resultText).params
    };
}

// Funció per a la Connexió 2 (Agent amb Knowledge Base)
async function cridarAgent(text, sessionId) {
    const command = new InvokeAgentCommand({
        agentId: process.env.AWS_AGENT_ID,
        agentAliasId: process.env.AWS_AGENT_ALIAS_ID,
        sessionId: sessionId,
        inputText: text,
    });

    const response = await agentClient.send(command);
    let fullResponse = "";
    for await (const chunk of response.completion) {
        if (chunk.chunk) fullResponse += Buffer.from(chunk.chunk.bytes).toString("utf-8");
    }

    return {
        tipus: "RESPOSTA_DIRECTA",
        text: fullResponse.trim()
    };
}