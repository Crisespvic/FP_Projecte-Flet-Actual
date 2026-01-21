import express from 'express';
import cors from 'cors';
import routes from './routes/aws_routes.js';
import fpRoutes from './routes/fp_routes.js';
import chatRoutes from './routes/chat_routes.js';
import normalitzador from './services/normalitzador.js';
import dotenv from 'dotenv';

dotenv.config();

const app = express();

// Habilitar CORS
app.use(cors());

// Middleware per parsejar JSON
app.use(express.json());

// Ús de les rutes
app.use('/api/bedrock', routes);
app.use('/api/fp', fpRoutes);
app.use('/api/fp', chatRoutes);

const PORT = process.env.PORT || 3000;

// Funció per a arrancar el servidor de forma segura
async function startServer() {
    try {
        // Inicialitzem el normalitzador abans que l'usuari puga fer consultes
        // Això omple els motors de Fuse.js amb les localitats, famílies, etc.
        await normalitzador.inicialitzar();

        app.listen(PORT, () => {
            console.log(`🚀 Servidor corrent en http://localhost:${PORT}`);
            console.log(`✅ Normalitzador de dades preparat.`);
        });
    } catch (error) {
        console.error("❌ No s'ha pogut iniciar el servidor:", error);
        process.exit(1);
    }
}

startServer();