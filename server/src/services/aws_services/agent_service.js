import { BedrockAgentRuntimeClient, InvokeAgentCommand } from "@aws-sdk/client-bedrock-agent-runtime";
import { fromIni } from "@aws-sdk/credential-providers";
import dotenv from "dotenv";

dotenv.config();

const REGION = process.env.AWS_REGION;
const credentials = fromIni({ profile: process.env.AWS_PROFILE });

// Canviem al client d'Agents
const agentClient = new BedrockAgentRuntimeClient({
  region: REGION,
  credentials
});

/**
 * Funció que connecta amb l'Agent de Bedrock.
 * L'Agent ja té el SYSTEM_PROMPT configurat a la consola d'AWS.
 */
export const buscadorDeConeixenement = async (missatgeUsuari, sessionId = "sessio-temporal1") => {
  try {
    const command = new InvokeAgentCommand({
      agentId: process.env.AWS_AGENT_ID,
      agentAliasId: process.env.AWS_AGENT_ALIAS_ID,
      sessionId: sessionId,
      inputText: missatgeUsuari,
    });

    const response = await agentClient.send(command);

    // Recollim el stream de dades que envia l'Agent
    let textComplet = "";
    for await (const chunk of response.completion) {
      if (chunk.chunk) {
        const bytes = chunk.chunk.bytes;
        textComplet += Buffer.from(bytes).toString("utf-8");
      }
    }
    // Retornem directament el resultat de l'Agent
    // No fem comprovacions de tipus, això ja s'ha decidit abans
    return textComplet.trim();

  } catch (error) {
    console.error("Error Agent Bedrock:", error);
    throw new Error("No s'ha pogut obtenir resposta de l'Agent d'AWS");
  }
};

