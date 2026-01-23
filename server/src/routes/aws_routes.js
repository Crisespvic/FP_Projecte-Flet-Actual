import express from 'express';
import { handleChat } from '../controllers/aws_controllers/aws_router_controller.js';

const router = express.Router();

// Ruta del agent interpret 
router.post('/chat', handleChat);

export default router;