import flet as ft
import flet_map as ftm
from controllers.chat_controller2 import processar_pregunta
from models.fp_models import Targeta
import base64
import asyncio

class ChatTab(ft.Container):
    def __init__(self, page: ft.Page, ref_map_fp=None, ref_map_ce=None):
        super().__init__() 
        self._page = page
        self.expand = True
        self.padding = 20
        # Referències de les pestanyes del main FpApp
        self.map_container_fp = ref_map_fp
        self.map_container_ce = ref_map_ce
        

        # llista de tuples de lat i lon per al mapa de punts multiples en la pestanya del chatbot
        self.lat_lon_list = []

        self.conversa_per_exportar = []
        
        # 1. Columna del Xat (Esquerra)
        self.chat_history = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            expand=True, 
            spacing=15
        )
        
        # 2. Input de l'usuari
        self.user_input = ft.TextField(
            hint_text="Escriu la teua pregunta...",
            expand=True, 
            border_radius=25,
            filled=True,
            border_color="blue-800",
            autofocus=True
        )
        self.user_input.on_submit = self.send_message

        # 3. Mapa (Dreta)
        self.map_container = ft.Ref[ft.Container]()
        self.map_widget = ftm.Map(
            expand=True,
            initial_center=ftm.MapLatitudeLongitude(39.48, -0.37),
            initial_zoom=8,
            interaction_configuration=ftm.InteractionConfiguration(flags=ftm.InteractionFlag.ALL),
            layers=[
                ftm.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    on_image_error=lambda e: print("TileLayer Error")
                )
            ]
        )
        

        # ESTRUCTURA DE LA PÀGINA
        # Botons de la pàgina
        self.export_btn = ft.IconButton(
            icon=ft.Icons.PICTURE_AS_PDF,
            icon_size=40,
            icon_color="red-800",
            tooltip="Exportar resum (HTML/PDF)",
        )
        self.export_btn.on_click=self.exportar_a_html

        self.send_btn = ft.IconButton(
            ft.Icons.SEND_ROUNDED, 
            icon_color="blue-800",
            icon_size=30
        )
        self.send_btn.on_click=self.send_message


        self.content = ft.Column([
            # Títol
            ft.Row([
                ft.Text("Assistent Virtual FP", size=24, weight="bold", color="blue-800"),
                self.export_btn
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            ft.Divider(height=1, color="grey-300"),
            
            # ÀREA DIVIDIDA (Xat + Input a l'esquerra, Mapa a la dreta)
            ft.Row([
                # Columna de l'Esquerra: Xat + Barra d'entrada
                ft.Column([
                    ft.Container(
                        content=self.chat_history,
                        expand=True, # El xat ocupa l'espai sobrant
                        padding=10,
                    ),
                    # BARRA D'ENTRADA (Dins de la secció del xat)
                    ft.Row([
                        self.user_input, 
                        self.send_btn
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], expand=1, alignment=ft.MainAxisAlignment.START), 

                ft.VerticalDivider(width=1, color=ft.Colors.BLUE_100),
                
                # Contenidor del Mapa (Dreta)
                ft.Container(
                    ref=self.map_container,
                    expand=1,
                    border=ft.border.all(1, ft.Colors.BLUE_GREY_200),
                    border_radius=15,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=self.map_widget
                )
            ], expand=True)
        ], expand=True)

    async def send_message(self, e):
        if not self.user_input.value.strip(): return
        
        user_text = self.user_input.value

        # Guarda la conversa
        self.conversa_per_exportar.append({"rol": "usuari", "text": user_text})
        
        # NETEJEM la llista de coordenades per a la nova consulta
        self.lat_lon_list = []
        
        # (Codi d'afegir missatge de l'usuari igual...)
        self.chat_history.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Text(user_text, color="white"),
                    bgcolor=ft.Colors.GREY_800,
                    padding=15,
                    border_radius=ft.border_radius.only(
                        top_left=20, top_right=20, bottom_left=20, bottom_right=2
                    ),
                    width=400, 
                )
            ], alignment=ft.MainAxisAlignment.END)
        )
        
        self.user_input.value = ""
        await self.user_input.focus()
        self.page.update()

        try:
            resposta = processar_pregunta(user_text)
            if isinstance(resposta, list):
                for result in resposta:
                    # Guarda les dades per al Html
                    self.conversa_per_exportar.append({
                        "rol": "model",
                        "centre": result.nom,
                        "cicle": result.nom_cicle,
                        "grau": result.grau,
                        "localitat": result.localitat,
                        "direccio": result.direccio, # Nou
                        "tel": result.telefon,
                        "web": result.web,           # Nou
                        "familia": result.familia,
                        "regim": result.regim,       # Nou
                        "torn": result.torn          # Nou
                    })
                    # Afegim a la llista si té coordenades
                    if result.latitud and result.longitud:
                        self.lat_lon_list.append((result.latitud, result.longitud))
                    
                    self.chat_history.controls.append(self.create_card(result, on_map_click=self.map_update))

                # GENERAR EL MAPA MULTIPLE
                if self.lat_lon_list:
                    await self.generar_mapa_multiple(self.lat_lon_list, multiple_coords=True)
            else:
                self.chat_history.controls.append(
                    ft.Text(f"{resposta}", size=18, color="red", italic=True)
                )
        except Exception as ex:
            print(f"Error intern: {ex}") # AIXÒ ET DIRÀ L'ERROR REAL EN CONSOLA
            self.chat_history.controls.append(
                ft.Text(f"S'ha produït un error al processar la informació.", color="red", italic=True)
            )
            
        self.page.update()
        
        await asyncio.sleep(0.5)
        if self.chat_history.controls:
            # Utilitzem offset=-1 que força el càlcul fins al final real de tot el contingut actualitzat.
            await self.chat_history.scroll_to(
                offset=-1, 
                duration=800,
                curve=ft.AnimationCurve.DECELERATE
            )


    def create_card(self, centre: Targeta, on_map_click, tipus_vista="xat"):
        # Gestionem la URL de la web per al botó 
        web_url = centre.web if centre.web else "Web no disponible"

        self.web_btn = ft.TextButton(
            "Visitar la Web",
            style=ft.ButtonStyle(padding=0), 
            tooltip="Pàgina Web del Centre"
        )
        self.web_btn.on_click = lambda e: asyncio.create_task(e.page.launch_url(web_url))

        self.map_btn = ft.ElevatedButton(
            "Veure en el mapa",
            icon=ft.Icons.MAP_OUTLINED,
            tooltip="Ubicació del centre",
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor="#076350",
            )
        )
        self.map_btn.on_click = lambda _: asyncio.create_task(on_map_click(centre, tipus_vista))

        regim = ""
        torn = ""
        if centre.regim == "Público":
            regim = "PÚBLIC"
        else:
            regim = "CONCERTAT"
        
        if centre.torn == "Diurno" or centre.torn == "Nocturno":
            torn = "PRESENCIAL"
        else:
            torn = "SEMIPRESENCIAL"

        # Retornem la Card amb el teu disseny i lògica original
        return ft.Card(
            elevation=3,
            content=ft.Container(
                padding=15,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                content=ft.Column([
                    # Títol i Família
                    ft.Column([
                        ft.Text(centre.nom.upper() if centre.nom else "CENTRE", weight="bold", size=20, color=ft.Colors.BLUE_900),
                        ft.Text(f"Família: {centre.familia}", size=18, italic=True, color=ft.Colors.BLUE_GREY_600),
                    ], spacing=2),

                    ft.Divider(height=1, color=ft.Colors.BLUE_GREY_100),

                    # Informació del Cicle i Grau
                    ft.Text(f"{centre.grau} - {centre.nom_cicle}", weight="w600", size=18),

                    # Etiquetes de Règim i Torn
                    ft.Row([
                        ft.Container(
                            content=ft.Text(regim, size=14, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.RED_800 if regim=="CONCERTAT" else ft.Colors.GREEN_700,
                            padding=ft.padding.all(5),
                            border_radius=5
                        ),
                        ft.Container(
                            content=ft.Text(torn, size=14, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.ORANGE_800 if torn=="SEMIPRESENCIAL" else ft.Colors.BLUE_700,
                            padding=ft.padding.all(5),
                            border_radius=5
                        ),
                    ], spacing=10),

                    # Contacte i Ubicació
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.LOCATION_ON, size=16), 
                            ft.Text(f"{centre.direccio if centre.direccio else ''}, {centre.localitat}", size=14, expand=True)
                        ]),
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE, size=16), 
                            ft.Text(f"{centre.telefon if centre.telefon else 'No disponible'}", size=14),
                            ft.VerticalDivider() if centre.web else ft.Container(),
                            ft.Icon(ft.Icons.LANGUAGE, size=16) if centre.web else ft.Container(),
                            self.web_btn if centre.web else ft.Container()
                        ]),
                    ], spacing=5),

                    # Botó Mapa
                    ft.Row([
                        self.map_btn
                    ], alignment=ft.MainAxisAlignment.END)
                ], spacing=12)
            )
        )
    
    # --- LÒGICA DEL MAPA ---
    # Funció per marcar un punt en el mapa
    async def map_update(self, centre=None, tipus_vista="xat"):
        if not centre or not centre.latitud or not centre.longitud:
            return
        
        coords = [(float(centre.latitud), float(centre.longitud))]

        try:
            # Generem mapa amb les coordenades actuals
            await self.generar_mapa_multiple(coords)
            self._page.update()
                
        except (ValueError, TypeError) as e:
            print(f"Error en coordenadas: {e}")
            await self._page.update_async()


    async def generar_mapa_multiple(self, llista_coords, tipus_vista="xat", multiple_coords=False):
        
        # Escollim el map_widget correcte
        if tipus_vista == "fp" and self.map_container_fp:
            target_map = self.map_container_fp.current.content  # el map_widget dins del container FP
        elif tipus_vista == "ce" and self.map_container_ce:
            target_map = self.map_container_ce.current.content  # el map_widget dins del container CE
        else:
            target_map = self.map_widget
    
        # Creem la capa de marcadors si no existeix
        if not hasattr(target_map, "_marker_layer"):
            target_map._marker_layer = ftm.MarkerLayer(markers=[])
            target_map.layers.append(target_map._marker_layer)
        else:
            target_map._marker_layer.markers.clear()

        # Afegim els marcadors
        for lat, lon in llista_coords:
            try:
                target_map._marker_layer.markers.append(
                    ftm.Marker(
                        content=ft.Icon(ft.Icons.LOCATION_ON, color=ft.Colors.BLUE_500, size=36),
                        coordinates=ftm.MapLatitudeLongitude(float(lat), float(lon)),
                        expand=True
                    )
                )
            except Exception as e:
                print(f"Error afegint marcador ({lat}, {lon}): {e}")
                continue

        # Centrem el mapa en el primer marcador
        if multiple_coords:
            if llista_coords:
                lat0, lon0 = llista_coords[0]
                await target_map.move_to(destination=ftm.MapLatitudeLongitude(float(lat0), float(lon0)),zoom= 10)
            else:
                await target_map.center_on(point=ftm.MapLatitudeLongitude(39.47, -0.38), zoom=8)
        else:
            if llista_coords:
                lat0, lon0 = llista_coords[0]
                await target_map.move_to(destination=ftm.MapLatitudeLongitude(float(lat0), float(lon0)),zoom= 15)
            else:
                await target_map.center_on(point=ftm.MapLatitudeLongitude(39.47, -0.38), zoom=8)

        self._page.update()
    
    def exportar_a_html(self, e):
        if not self.conversa_per_exportar:
            return

        html_content = """
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Segoe UI', sans-serif; background-color: #f4f7f6; padding: 30px; color: #333; }
                .container { max-width: 850px; margin: auto; }
                .user-msg { background: #2c3e50; color: white; padding: 15px; border-radius: 12px 12px 0 12px; margin-bottom: 25px; margin-left: 15%; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
                .card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-left: 8px solid #076350; position: relative; }
                .title { color: #1a237e; font-size: 1.4em; margin: 0; font-weight: bold; text-transform: uppercase; }
                .familia { color: #666; font-style: italic; margin-top: 5px; font-size: 0.95em; }
                .cicle-info { font-size: 1.1em; margin: 15px 0; color: #000; font-weight: 600; }
                .badges-row { margin: 10px 0; }
                .badge { display: inline-block; padding: 4px 10px; border-radius: 6px; color: white; font-size: 0.85em; font-weight: bold; margin-right: 8px; text-transform: uppercase; }
                .public { background-color: #2e7d32; }
                .concertat { background-color: #c62828; }
                .torn { background-color: #1565c0; }
                .contact-info { margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; font-size: 0.9em; line-height: 1.6; color: #444; }
                .web-link { color: #076350; text-decoration: none; font-weight: bold; }
                @media print { .no-print { display: none; } body { background: white; padding: 0; } .card { box-shadow: none; border: 1px solid #ddd; page-break-inside: avoid; } }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 style="color: #076350; text-align: center; margin-bottom: 40px;">El meu Itinerari Formatiu</h1>
        """

        for item in self.conversa_per_exportar:
            if item["rol"] == "usuari":
                html_content += f'<div class="user-msg"><b>La meua pregunta:</b><br>{item["text"]}</div>'
            else:
                # Lògica de colors per al règim
                regim_text = item.get('regim') or "Públic"
                regim_class = "concertat" if "Concert" in regim_text or "Privat" in regim_text else "public"
                
                # Preparar la direcció i la web
                direccio = item.get('direccio') or "No disponible"
                web = item.get('web')
                web_html = f'<br>🌐 <a class="web-link" href="{web}" target="_blank">{web}</a>' if web and web != "Web no disponible" else ""

                html_content += f"""
                <div class="card">
                    <p class="title">{item['centre']}</p>
                    <p class="familia">Família: {item['familia']}</p>
                    
                    <p class="cicle-info">{item['grau']} - {item['cicle']}</p>
                    
                    <div class="badges-row">
                        <span class="badge {regim_class}">{regim_text}</span>
                        <span class="badge torn">{item.get('torn') or 'Presencial'}</span>
                    </div>
                    
                    <div class="contact-info">
                        📍 <b>Ubicació:</b> {direccio}, {item['localitat']}<br>
                        📞 <b>Telèfon:</b> {item['tel']}
                        {web_html}
                    </div>
                </div>
                """

        html_content += """
            </div>
            <script>
                window.onload = function() { 
                    setTimeout(() => { window.print(); }, 800); 
                };
            </script>
        </body>
        </html>
        """
        
        # procés de guardar i obrir
        import os, webbrowser
        path = os.path.abspath("resum_fp.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_content)
        webbrowser.open(f"file://{path}")