import normalitzador from '../../services/normalitzador.js';
import {modelParametritzador} from '../../services/aws_services/aws_ai_service.js';
import {getCentresPerCicleOFamilia} from '../fp_controller.js';

export const parametritzador = async (message) => {
    try {
        console.log("Ha arribat el missatge: "+message);
        const aiOutput = await modelParametritzador(message);
        const paramsNets = normalitzador.normalitzar(aiOutput.params);
        let dadesFinals;

        // Simulem l'objecte 'res' d'Express
        const resSimulat = {
            // Simulem la funció .json() per capturar les dades en la nostra variable
            json: (contingut) => {
                dadesFinals = contingut;
            },
            // Simulem .status() per si hi haguera un error (encara que no l'usarem molt ací)
            status: function(codi) {
                return this; 
            }
        };

        
        // Cridem a la funció passant el body simulat i el res simulat
        await getCentresPerCicleOFamilia({ body: paramsNets }, resSimulat);

        return {
            success: true,
            data: dadesFinals.data || [],
            message: dadesFinals.message || dadesFinals.msg || null
        };

    } catch (error) {
        console.error("Error en el xat:", error);
        throw error; 
    }
};