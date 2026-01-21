class Targeta:
    def __init__(self, nom, localitat, comarca, provincia, latitud, longitud, nom_cicle, familia, grau, torn, direccio=None, regim=None, telefon=None, web=None):
        self.nom = nom
        self.localitat = localitat
        self.comarca = comarca
        self.provincia = provincia
        self.direccio = direccio
        self.telefon = telefon
        self.web = web
        self.latitud = latitud
        self.longitud = longitud
        self.nom_cicle = nom_cicle
        self.grau = grau
        self.familia = familia
        self. regim = regim
        self.torn = torn
        

    @staticmethod
    def from_json(json_data):
        return Targeta(
            nom=json_data.get("centre"),
            localitat=json_data.get("localitat"),
            comarca=json_data.get("comarca"),
            provincia=json_data.get("provincia"),
            direccio=json_data.get("direccio"),
            telefon=json_data.get("telefon"),
            web=json_data.get("web"),
            latitud=json_data.get("latitud"),
            longitud=json_data.get("longitud"),
            nom_cicle=json_data.get("nom_cicle"),
            grau=json_data.get("grau"),
            familia=json_data.get("familia"),
            regim=json_data.get("regim_formatiu"),
            torn=json_data.get("torn")
        )

class Filtres:
    def __init__(self, provincies, comarques, localitats, families, graus):
        self.provincies = provincies
        self.comarques = comarques
        self.localitats = localitats
        self.families = families
        self.graus = graus

    @staticmethod
    def from_json(json_data):
        d = json_data.get("data", {})
        return Filtres(
            provincies=d.get("provincies", []),
            comarques=d.get("comarques", []),
            localitats=d.get("localitats", []),
            families=d.get("families", []),
            graus=d.get("graus", [])
        )

class Cicle:
    def __init__(self, id, nom, familia, grau):
        self.id = id
        self.nom = nom
        self.familia = familia
        self.grau = grau

    @staticmethod
    def from_json(json_data):
        """Converteix un diccionari JSON en un objecte Cicle"""
        return Cicle(
            id=json_data.get("id"),
            nom=json_data.get("nom_cicle"),
            familia=json_data.get("familia"),
            grau=json_data.get("grau")
        )

    def __str__(self):
        return f"{self.nom} ({self.grau})"