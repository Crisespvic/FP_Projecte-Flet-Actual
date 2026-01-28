import { BedrockRuntimeClient, ConverseCommand } from "@aws-sdk/client-bedrock-runtime";
import { fromIni } from "@aws-sdk/credential-providers";
import dotenv from "dotenv";

dotenv.config();

// Configuració Bedrock
const REGION = process.env.AWS_REGION;
const credentials = fromIni({ profile: process.env.AWS_PROFILE });

const runtime = new BedrockRuntimeClient({
  region: REGION,
  credentials
});

const SYSTEM_PROMPT = `
Ets un classificador d'intencions especialitzat en Formació Professional (FP). La teua única missió és analitzar la consulta de l'usuari i determinar quina via d'execució és la correcta.

EXISTEIXEN DOS TIPUS DE RUTES:

1- {"type":"Parametritzada"}: 
S'utilitza QUAN i NOMÉS QUAN l'usuari demana llistats concrets basats en filtres geogràfics o de catàleg. L'usuari ja sap què vol o on ho vol.
Paraules clau: "On puc estudiar...", "Quins centres...", "Llista de...", "A la localitat de...".
Exemple: "Busca'm instituts a Castelló que facen cuina".

2- {"type":"Coneixement"}:
S'utilitza per a consultes que requereixen raonament, explicació de normativa o ORIENTACIÓ PERSONALITZADA. 
Aquesta ruta inclou:
- Orientació inicial: L'usuari descriu qui és o què li agrada però NO demana un llistat de centres encara (ex: "Tinc 16 anys i m'agraden els ordinadors").
- Dubtes de procediment: Requisits, notes de tall, terminis, proves d'accés.
- Contingut: Què s'estudia en un cicle, quines eixides té, o diferències entre cicles.

INSTRUCCIONS DE DECISIÓ CRÍTICA:
- Si l'usuari expressa un perfil personal (edat, títols que té) o un gust/afició sense demanar una ubicació específica, selecciona SEMPRE "Coneixement".
- L'orientació acadèmica és una tasca de "Coneixement", no de base de dades.

Respon exclusivament en format JSON pur:
{"type":"Parametritzada"} o {"type":"Coneixement"}
`.trim();

/**
 * Funció per cridar al model orquestrador o ruter
 */
export const interpretarPregunta = async (missatgeUsuari) => {
  
  let jsonDades;
  
  try {
    const command = new ConverseCommand({
      modelId: process.env.AWS_MODEL_ID0,
      system: [{ text: SYSTEM_PROMPT }],
      messages: [
        {
          role: "user",
          content: [{ text: missatgeUsuari }]
        }
      ],
      inferenceConfig: {
        maxTokens: 500,
        temperature: 0.1,
        topP: 0.9
      }
    });



    const response = await runtime.send(command);

    let text = response.output.message.content
      .map(part => part.text ?? "")
      .join("")
      .trim();

    // Neteja per si el model posa ```json ... ``` o punts i coma
    text = text.replace(/```json|```/g, "").replace(/;/g, "").trim();

    jsonDades = JSON.parse(text);

    // RETORNEM NOMÉS EL STRING ("Parametritzada" o "Coneixement")
    // Així el teu IF en handleChat funcionarà correctament.
    return jsonDades.type;

  } catch (error) {
    console.error("❌ Error Bedrock:", error);
    // Mantenim el mateix comportament d'error que tenies amb Gemini
    jsonDades = "Error";
    return jsonDades;
  }
};