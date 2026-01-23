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
Ets un expert en detectar que pretén obtindre l'usuari i quin tipus de pregunta ha fet.
Hi ha dos tipus de preguntes:

1- "Type":"Parametritzada" : Preguntes on l'usuari pretén obtindre quins cicles de FP o cursos de especialització CE (Màsters) pot estudiar de diferents graus, families o ubicacións.
Exemples:
-"On puc estudiar un cicle de fp mitjà de electricitat?"
-"Quins cicles de fp superior de hosteleria hi han a la Marina Alta?"
-"Màster de grau mitjà en mecànica a la provincia d'Alacant"
-"Especialització de Informàtica a Gandia?"
-"On puc estudiar Desarrollo de Aplicaciones Web a la Safor?"

2- "Type":"Coneixement" : Preguntes amb les quals l'usuari pretén obtindre informació extra sobre educació de FP o Especialització,
més enllà de del tipus de pregunta 1. 
Exemples:
- Requisits i proves d'accés per a cada nivell
- Normativa autonòmica i estatal aplicable
- Terminis de matriculació i sol·licituds
- Estructura curricular: mòduls, hores setmanals i totals
- Centres educatius autoritzats
- Eixides professionals i continuïtat acadèmica
- Procediments administratius i documentació necessària
- Orientació per a alumnes amb característiques específiques

La teua missió es respondre solament de quin tipus de es la pregunta que t'acaben de formular, en format JSON pur.
Exemples de resposta:
{"type":"Parametritzada"};
{"type":"Coneixement"};
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