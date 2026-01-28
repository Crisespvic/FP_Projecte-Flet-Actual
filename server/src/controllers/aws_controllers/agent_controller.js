import { buscadorDeConeixenement } from '../../services/aws_services/agent_service.js';
import dotenv from "dotenv";

dotenv.config();

// Configuració Bedrock
const SESSION_ID = process.env.AWS_AGENT_SESSION_ID;
export const biblioteca = async (message) => {
    try {
        // Cridem directament a l'agent d'AWS
        const aiResponse = await buscadorDeConeixenement(message, SESSION_ID);

        // Retornem la resposta estructurada per a que handleChat la puga enviar
        return {
            success: true,
            data: [],
            message: aiResponse
        };

    } catch (error) {
        console.error("Error en la funció biblioteca:", error);
        throw error;
    }
};