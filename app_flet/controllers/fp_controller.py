from services.offer_service import get_cicles_filtrats,get_cursos_filtrats, cercar_oferta
from services.fill_filter_service import get_filtres, get_all_cicles_fp, get_all_cicles_ce, get_comarques_per_provincia, get_localitats_per_comarca, get_localitats_per_provincia
from models.fp_models import Targeta, Filtres, Cicle

def obtenir_tots_els_filtres(tipus):
    """Retorna un objecte Filtres amb les llistes per als dropdowns"""
    json_data = get_filtres(tipus)
    if json_data.get("success"):
        return Filtres.from_json(json_data)
    return Filtres([], [], [], [], [])

def obtenir_tots_els_cicles_fp():
    """Retorna una llista d'objectes Cicle per als Dropdowns"""
    # Obtenim el diccionari complet
    json_res = get_all_cicles_fp()
    
    # Extraiem la llista que està dins de la clau "data"
    llista_dades = json_res.get("data", [])
    
    # Comprovem si tenim una llista i fem la conversió
    if isinstance(llista_dades, list):
        return [Cicle.from_json(item) for item in llista_dades]
    
    return []

def obtenir_tots_els_cicles_ce():
    """Retorna una llista d'objectes Cicle per als Dropdowns"""
    # Obtenim el diccionari complet
    json_res = get_all_cicles_ce()
    
    # Extraiem la llista que està dins de la clau "data"
    llista_dades = json_res.get("data", [])
    
    # Comprovem si tenim una llista i fem la conversió
    if isinstance(llista_dades, list):
        return [Cicle.from_json(item) for item in llista_dades]
    
    return []

def obtenir_cicles_filtrats(provincia=None, comarca=None, localitat=None, familia=None, grau=None):
    """Retorna una llista d'objectes Cicle per als Dropdowns de la pestanya de cicles de FP"""
    # Obtenim el diccionari complet
    json_res = get_cicles_filtrats(provincia, comarca, localitat, familia, grau)
    
    # Extraiem la llista que està dins de la clau "data"
    llista_dades = json_res.get("data", [])
    
    # Comprovem si tenim una llista i fem la conversió
    if isinstance(llista_dades, list):
        return [Cicle.from_json(item) for item in llista_dades]
    
    return []

def obtenir_cursos_filtrats(provincia=None, comarca=None, localitat=None, familia=None, grau=None):
    """Retorna una llista d'objectes Cicle per als Dropdowns de la pestanya de Cursos d'Especialització"""
    # Obtenim el diccionari complet
    json_res = get_cursos_filtrats(provincia, comarca, localitat, familia, grau)
    
    # Extraiem la llista que està dins de la clau "data"
    llista_dades = json_res.get("data", [])
    
    # Comprovem si tenim una llista i fem la conversió
    if isinstance(llista_dades, list):
        return [Cicle.from_json(item) for item in llista_dades]
    
    return []

def executar_cerca_oferta(tipus, pagina, provincia=None, comarca=None, localitat=None, familia=None, grau=None, id_cicle=None):
    """Retorna un diccionari amb els objectes Targeta i informació de paginació."""

    json_data = cercar_oferta(tipus, pagina, provincia, comarca, localitat, familia, grau, id_cicle)
    
    if json_data.get("success"):
        # 1. Convertim les dades en objectes Targeta
        llista_objectes = [Targeta.from_json(item) for item in json_data.get("data", [])]
        
        # 2. Retornem un diccionari estructurat
        return {
            "oferta": llista_objectes,
            "total": json_data.get("total", 0),
            "pagines_totals": json_data.get("pagines_totals", 1)
        }
    
    # En cas d'error o buit, retornem l'estructura mínima per evitar errors a la UI
    return {
        "oferta": [],
        "total": 0,
        "pagines_totals": 1
    }

def obtenir_comarques(provincia=None):
    """
    Retorna la llista de comarques filtrada per província demanant-ho a l'API.
    """
    if not provincia or provincia == "NINGUNA":
        # Si no hi ha província, retorna totes les comarques amb la funció get_filtres
        json_data = get_filtres()
        return json_data.get("data", {}).get("comarques", [])
    
    comarques = get_comarques_per_provincia(provincia)
    
    return comarques

def obtenir_localitats_de_comarca(comarca=None):
    """
    Retorna la llista de localitats filtrada per comarca.
    """
    if not comarca or comarca == "NINGUNA":
        # Si no hi ha comarca, retorna totes les localitats amb la funció get_filtres
        json_data = get_filtres()
        return json_data.get("data", {}).get("localitats", [])
    
    localitats = get_localitats_per_comarca(comarca)
    
    return localitats

def obtenir_localitats_de_provincia(provincia=None):
    """
    Retorna la llista de localitats filtrada per província.
    """
    if not provincia or provincia == "NINGUNA":
        # Si no hi ha provincia, retorna totes les localitats amb la funció get_filtres
        json_data = get_filtres()
        return json_data.get("data", {}).get("localitats", [])
    
    localitats = get_localitats_per_provincia(provincia)
    
    return localitats