import { buscadorDeConeixenement } from '../../services/aws_services/agent_service.js';

export const biblioteca = async (message) => {
    try {
        console.log("Ha arribat el missatge: "+message);
        // Cridem directament a l'agent d'AWS
        const aiResponse = await buscadorDeConeixenement(message);

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