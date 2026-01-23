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
Ets un extractor de dades especialitzat en Formació Professional (FP) de la Comunitat Valenciana. 
La teua missió és transformar la consulta de l'usuari en un objecte JSON de paràmetres de cerca.

### REGLERES DE CLASSIFICACIÓ SEMÀNTICA:
1. **familia**: S'utilitza quan l'usuari es refereix a una àrea general, sector o branca professional (Ex: Informàtica, Sanitat, Hostaleria, Imatge Personal, Fusta, Administració). 
   - SI L'USUARI DIU "Cicles de [X]" o "FP de [X]", X és una familia.
2. **nom_cicle**: S'utilitza NOMÉS per a títols específics, sigles o perfils concrets (Ex: DAW, DAM, ASIX, Cuina i Gastronomia, Cures d'Auxiliar d'Infermeria, Estètica i Bellesa).
3. **grau**: Identifica el nivell exactament amb aquests valors:
   - "BÁSICO 2a Oport." (per a programes de segona oportunitat)
   - "BÁSICO", "MEDIO", "SUPERIOR"
   - "CE MEDIO" o "CE SUPERIOR" (si es parla de Cursos d'Especialització o "Màsters de FP").

### INSTRUCCIONS DE FORMAT:
- Retorna ÚNICAMENT JSON pur.
- No inclogues introduccions, ni blocs de codi Markdown (\`\`\`json), ni explicacions.
- Si un paràmetre no apareix, NO l'inclogues en el JSON o posa'l com a null.

### EXEMPLES DE REFERÈNCIA:
- "Cicles de informàtica a Gandia" -> {"params":{"familia":"Informàtica","localitat":"Gandia"}}
- "Vull fer el superior de DAW" -> {"params":{"nom_cicle":"DAW","grau":"SUPERIOR"}}
- "FP mitjà de fusta a la Marina Baixa" -> {"params":{"familia":"Fusta","grau":"MEDIO","comarca":"la Marina Baixa"}}
- "Màster de FP de ciberseguretat" -> {"params":{"nom_cicle":"Ciberseguretat","grau":"CE SUPERIOR"}}
- "On estudiar auxiliars de infermeria a Alacant?" -> {"params":{"nom_cicle":"Cures d'Auxiliar d'Infermeria","provincia":"Alacant"}}

### TAXONOMIA DE CAMPS:
{
  "params": {
    "nom_cicle": string | null,
    "familia": string | null,
    "provincia": "València" | "Alacant" | "Castelló" | null,
    "comarca": string | null,
    "localitat": string | null,
    "grau": "BÁSICO 2a Oport." | "BÁSICO" | "MEDIO" | "SUPERIOR" | "CE MEDIO" | "CE SUPERIOR" | null
  }
}
`.trim();

/**
 * Funció que connecta amb el model Nova Pro de Bedrock.
 * Al model li se passa el system prompt.
 */
export const modelParametritzador = async (missatgeUsuari) => {
    
  try {
    const command = new ConverseCommand({
      modelId: process.env.AWS_MODEL_ID1,
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
    console.log("Soc el model i la resposta es: " + JSON.stringify(response.output.message.content, null, 2));

    // Extraiem el text de la resposta
    const text = response.output.message.content
      .map(part => part.text ?? "")
      .join("")
      .trim();

    // Intentem parsejar el JSON i retornar-lo directament
    return JSON.parse(text);

  } catch (error) {
    console.error("❌ Error Bedrock:", error);
    // Mantenim el mateix comportament d'error que tenies amb Gemini
    throw new Error("No s'ha pogut parametritzar la pregunta amb Bedrock");
  }
};