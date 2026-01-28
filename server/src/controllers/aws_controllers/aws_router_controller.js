import {interpretarPregunta} from '../../services/aws_services/aws_router_model.js';
import {parametritzador} from '../aws_controllers/aws_controller.js';
import {biblioteca} from '../aws_controllers/agent_controller.js';

export const handleChat = async (req, res) => {
    try {
        const { message } = req.body;
        const tipus_pregunta = await interpretarPregunta(message);

        let resultat;
        if(tipus_pregunta === "Parametritzada"){
           resultat = await parametritzador(message);

        }
        else if (tipus_pregunta === "Coneixement"){
            resultat = await biblioteca(message);
        }
        else{
            resultat = { data: [], message: "Error: No s'ha pogut determinar el tipus de consulta." };
        }


        // Enviem la resposta real a l'aplicació
        res.json({
            success: true,
            // Fem servir l'encadenament opcional (?.) per seguretat
            data: resultat?.data || [],
            message: resultat?.message || resultat?.msg || null, 
            type: tipus_pregunta
        });

    } catch (error) {
        console.error("Error en el xat:", error);
        res.status(500).json({ success: false, error: error.message });
    }
};