import db from '../database/db.js';

// Obtenir les opcions per als dropdowns de la interfície de la pestanya FP al inici
export const getFiltresInicials = async (req, res) => {
    // Obtenim el paràmetre directament de la ruta
    const { tipus } = req.params; 

    try {
        const [provincies] = await db.db.promise().query('SELECT DISTINCT provincia FROM centre WHERE provincia IS NOT NULL ORDER BY provincia');
        const [comarques] = await db.db.promise().query('SELECT DISTINCT comarca FROM centre WHERE comarca IS NOT NULL ORDER BY comarca');
        const [localitats] = await db.db.promise().query('SELECT DISTINCT localitat FROM centre WHERE localitat IS NOT NULL ORDER BY localitat');
        const [families] = await db.db.promise().query('SELECT DISTINCT familia FROM titulacio WHERE familia IS NOT NULL ORDER BY familia');
        let consultaGraus;

        if (tipus?.toUpperCase() === 'CE') {
            consultaGraus = "SELECT DISTINCT grau FROM titulacio WHERE grau IN ('CE MEDIO', 'CE SUPERIOR') ORDER BY grau";
        } else {
            consultaGraus = "SELECT DISTINCT grau FROM titulacio WHERE grau IS NOT NULL AND grau NOT IN ('CE MEDIO', 'CE SUPERIOR') ORDER BY grau";
        }

        const [graus] = await db.db.promise().query(consultaGraus);

        res.json({
            success: true,
            data: {
                provincies: provincies.map(p => p.provincia),
                comarques: comarques.map(c => c.comarca),
                localitats: localitats.map(l => l.localitat),
                families: families.map(f => f.familia),
                graus: graus.map(g => g.grau)
            }
        });
    } catch (error) {
        console.error('Error carregant filtres:', error);
        res.status(500).json({ success: false, message: 'Error al carregar els filtres' });
    }
};

// Cercar oferta de FP segons els filtres seleccionats
export const cercarOferta = async (req, res) => {
    const { tipus, pagina, provincia, comarca, localitat, familia, grau, id_cicle } = req.body;

    const midaPagina = 10;
    const saltar = (pagina - 1) * midaPagina;

    // 1. Construïm la part COMÚ de la consulta (els JOINs i el WHERE)
    let baseSql = `
        FROM oferta o
        JOIN centre c ON o.codcen = c.codi
        JOIN titulacio t ON o.id_titulacio = t.id
        WHERE 1=1`;
    
    const paramsFiltres = [];

    if (tipus === "FP") {
        baseSql += " AND t.grau IN ('BÁSICO', 'BÁSICO 2a Oport.', 'MEDIO', 'SUPERIOR')";
    } else if (tipus === "CE") {
        baseSql += " AND t.grau IN ('CE MEDIO', 'CE SUPERIOR')";
    }

    if (provincia && provincia !== "---NINGUNA---") {
        baseSql += " AND c.provincia = ?";
        paramsFiltres.push(provincia);
    }
    
    if (comarca && comarca !== "---NINGUNA---") {
        baseSql += " AND c.comarca = ?";
        paramsFiltres.push(comarca);
    }
    
    if (localitat && localitat !== "---NINGUNA---") {
        baseSql += " AND c.localitat = ?";
        paramsFiltres.push(localitat);
    }

    if (familia && familia !== "---NINGUNA---") {
        baseSql += " AND t.familia = ?";
        paramsFiltres.push(familia);
    }
    
    if (grau && grau !== "---NINGÚN---") {
        baseSql += " AND t.grau = ?";
        paramsFiltres.push(grau);
    }
    
    if (id_cicle && id_cicle !== "---NINGÚN---") {
        baseSql += " AND t.id = ?";
        paramsFiltres.push(id_cicle);
    }

    try {
        // 2. EXECUTEM EL COUNT (Total de resultats sense LIMIT)
        const countSql = `SELECT COUNT(*) as total ${baseSql}`;
        const totalResult = await db.query(countSql, paramsFiltres);
        const totalRegistres = totalResult[0].total;

        // 3. EXECUTEM LA CERCA DE DADES (Amb LIMIT i OFFSET)
        let dataSql = `
            SELECT 
                c.nom AS centre, c.localitat, c.comarca, c.provincia, 
                c.direccio, c.telefon, c.web, c.latitud, c.longitud,
                t.nom_cicle, t.grau, t.familia, o.regim_formatiu, o.torn
            ${baseSql} 
            ORDER BY c.nom ASC LIMIT ? OFFSET ?`;
        
        // Afegim els paràmetres de paginació als filtres existents
        const paramsData = [...paramsFiltres, midaPagina, saltar];
        const resultats = await db.query(dataSql, paramsData);

        // 4. RETORNEM LES DUES COSES
        res.json({ 
            success: true, 
            data: resultats, 
            total: totalRegistres,
            pagines_totals: Math.ceil(totalRegistres / midaPagina) 
        });

    } catch (error) {
        console.error('Error en la cerca:', error);
        res.status(500).json({ success: false, message: error.message });
    }
};

// Obtenir comarques filtrades per província
export const getComarquesPerProvincia = async (req, res) => {
    const { provincia } = req.params;
    try {
        const [rows] = await db.db.promise().query(
            'SELECT DISTINCT comarca FROM centre WHERE provincia = ? AND comarca IS NOT NULL ORDER BY comarca',
            [provincia]
        );
        res.json({ success: true, data: rows.map(r => r.comarca) });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
};

// Obtenir comarques filtrades per Comarca
export const getLocalitatsPerComarca = async (req, res) => {
    const comarca = decodeURIComponent(req.params.comarca);
    
    try {
        const sql = `
            SELECT DISTINCT c.localitat 
            FROM centre c
            INNER JOIN oferta o ON c.codi = o.codcen
            WHERE c.comarca = ? 
              AND c.localitat IS NOT NULL 
            ORDER BY c.localitat`;

        const [rows] = await db.db.promise().query(sql, [comarca]);

        
        // Enviem la llista de noms al frontend
        res.json({ 
            success: true, 
            data: rows.map(l => l.localitat) 
        });
    } catch (error) {
        console.error('Error a getLocalitatsPerComarca:', error);
        res.status(500).json({ success: false, message: error.message });
    }
};

// Obtenir localitats amb oferta filtrades per Província
export const getLocalitatsPerProvincia = async (req, res) => {
    const provincia = decodeURIComponent(req.params.provincia);
    
    try {
        const sql = `
            SELECT DISTINCT c.localitat 
            FROM centre c
            INNER JOIN oferta o ON c.codi = o.codcen
            WHERE c.provincia = ? 
              AND c.localitat IS NOT NULL 
            ORDER BY c.localitat`;

        const [rows] = await db.db.promise().query(sql, [provincia]);
        
        res.json({ 
            success: true, 
            data: rows.map(l => l.localitat) 
        });
    } catch (error) {
        res.status(500).json({ success: false, message: error.message });
    }
};

// Obtindre els centres d'un cicle o curs
export const getCentresPerCicleOFamilia = async (req, res) => {
    // Afegim 'familia' a la desestructuració
    const { nom_cicle, familia, provincia, comarca, localitat, grau } = req.body;

    const teFiltreGeografic = provincia || comarca || localitat;
    const teFiltreContingut = nom_cicle || familia || grau;

    if (!teFiltreGeografic && !teFiltreContingut) {
        return res.json({ 
            success: true, 
            data: [], 
            message: "Per favor, indica una localitat, comarca o província per a poder mostrar-te els cicles disponibles." 
        });
    }

    let sql = `
        SELECT DISTINCT 
            c.nom AS centre, 
            c.localitat, 
            c.comarca, 
            c.provincia, 
            c.direccio, 
            c.telefon, 
            c.web, 
            c.latitud, 
            c.longitud,
            t.nom_cicle, 
            t.grau,
            t.familia,
            o.regim_formatiu,
            o.torn
        FROM centre c
        JOIN oferta o ON c.codi = o.codcen
        JOIN titulacio t ON o.id_titulacio = t.id
        WHERE 1=1`; // Truc per a anar encadenant ANDs fàcilment
    
    const params = [];

    // Lògica de cerca principal (Cicle i/o Família)
    // Si Gemini/Fuse detecten ambdós, filtrarà per ambdós (AND)
    if (nom_cicle) {
        sql += ` AND t.nom_cicle LIKE ?`;
        params.push(`%${nom_cicle}%`);
    }

    if (familia) {
        sql += ` AND t.familia = ?`;
        params.push(familia);
    }

    // Filtres geogràfics (igual que els tenies)
    if (provincia) {
        sql += ` AND c.provincia = ?`;
        params.push(provincia);
    }
    if (comarca) {
        sql += ` AND c.comarca = ?`;
        params.push(comarca);
    }
    if (localitat) {
        sql += ` AND c.localitat = ?`;
        params.push(localitat);
    }
    if (grau) {
        sql += ` AND t.grau = ?`;
        params.push(grau);
    }

    sql += ` ORDER BY c.provincia, c.localitat ASC`;
    
    try {
        const [resultats] = await db.db.promise().query(sql, params);
        
        if (resultats.length === 0) {
            return res.json({ 
                success: true, 
                message: "No s'han trobat centres amb aquests criteris.",
                data: [] 
            });
        }

        res.json({ success: true, data: resultats });
    } catch (error) {
        console.error('Error en getCentresPerCicleOFamilia:', error);
        res.status(500).json({ success: false, message: error.message });
    }
};