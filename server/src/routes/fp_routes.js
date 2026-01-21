import express from 'express';
import { getFiltresInicials, cercarOferta, getComarquesPerProvincia, getLocalitatsPerComarca, getLocalitatsPerProvincia} from '../controllers/fp_controller.js';
import {getTotesTitulacionsFP, getTotesTitulacionsCE, getCiclesFiltrats, getCursosFiltrats} from '../controllers/cicles_controller.js';

const router = express.Router();

// Aquesta ruta s'executarà quan carregue l'app de Flet
router.get('/filtres/:tipus', getFiltresInicials);

// Aquesta quan l'usuari polse el botó de "Cercar"
router.post('/cercar', cercarOferta);

// Comarques i localitats en seleccionar províncies i/o comarca
router.get('/comarques/:provincia', getComarquesPerProvincia);
router.get('/localitats/:comarca', getLocalitatsPerComarca);
router.get('/toteslocalitats/:provincia', getLocalitatsPerProvincia);

// Titulacions segons diferents filtres
router.get('/cicles', getTotesTitulacionsFP);
router.get('/cursos', getTotesTitulacionsCE);
router.post('/cicles', getCiclesFiltrats);
router.post('/cursos', getCursosFiltrats);



export default router;