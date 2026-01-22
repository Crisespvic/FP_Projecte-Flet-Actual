import flet as ft
import flet_map as ftm
from controllers.fp_controller import obtenir_tots_els_filtres, executar_cerca_oferta, obtenir_comarques, obtenir_localitats_de_comarca, obtenir_localitats_de_provincia, obtenir_tots_els_cicles_fp, obtenir_tots_els_cicles_ce, obtenir_cicles_filtrats, obtenir_cursos_filtrats
from models.ai_models import ChatTab
import asyncio

class FpApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Orientat FP - Comunitat Valenciana"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Referències per a actualització dinàmica
        self.map_container_fp = ft.Ref[ft.Container]()
        self.map_container_ce = ft.Ref[ft.Container]()
        self.results_col_fp = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            expand=True, 
            spacing=10, 
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self.results_col_ce = ft.Column(
            scroll=ft.ScrollMode.AUTO, 
            expand=True, 
            spacing=10, 
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        
        # Carreguem filtres inicials per als dropdown de la pestanya FP
        self.filtres_globals_fp = obtenir_tots_els_filtres(tipus="FP")

        # Carreguem filtres inicials per als dropdown de la pestanya CE
        self.filtres_globals_ce = obtenir_tots_els_filtres(tipus="CE")

        # Carrega la llista d'objectes Cicle
        self.cicles_globals_fp = obtenir_tots_els_cicles_fp()

        # Carrega la llista d'objectes Cicle
        self.cicles_globals_ce = obtenir_tots_els_cicles_ce()

        # Llistes buides per a les tuples (lat,lon)
        self.lat_lon_fplist=[]
        self.lat_lon_celist=[]

        # Recompte de resultats
        self.fp_result_text = ft.Text(f"0 resultats", size=24, weight="bold")
        self.ce_result_text = ft.Text(f"0 resultats", size=24, weight="bold")

        # Paginació de resultats
        self.num_pagina_actual_fp = 1
        self.num_pagina_actual_ce = 1

        # Total de resultats trobats en la cerca
        self.total_res_fp = 0
        self.total_res_ce = 0

        # Total de pàgines de resultats
        self.total_pages_fp = 0
        self.total_pages_ce = 0

        # vista i lògica del chatbot
        self.vista_chatbot = ChatTab(
            page=self.page, 
            ref_map_fp=self.map_container_fp, 
            ref_map_ce=self.map_container_ce
        )
        
        self.setup_ui()

    def setup_ui(self):
        # --- DEFINICIÓ DE DROPDOWNS FP---
        self.drop_provincia_fp = ft.DropdownM2(
            label="Província",
            hint_text="Provincia",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(prov.upper()) for prov in self.filtres_globals_fp.provincies]
        )
        self.drop_provincia_fp.on_change=self.actualitzar_comarques

        self.drop_comarca_fp = ft.DropdownM2(
            label="Comarca",
            hint_text="Comarca",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(comarca) for comarca in self.filtres_globals_fp.comarques]
        )
        self.drop_comarca_fp.on_change=self.actualitzar_localitats

        self.drop_localitat_fp = ft.DropdownM2(
            label="Localitat",
            hint_text="Localitat",
            expand=True, 
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(localitat) for localitat in self.filtres_globals_fp.localitats]
        )

        self.drop_familia_fp = ft.DropdownM2(
            label="Familia",
            hint_text="Familia",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(familia) for familia in self.filtres_globals_fp.families]  
        )
        self.drop_familia_fp.on_change=lambda _: self.actualitzar_dropdown_cicles_fp()

        self.drop_grau_fp = ft.DropdownM2(
            label="Grau",
            hint_text="Grau",
            expand=True, 
            options=[ft.dropdownm2.Option("---NINGÚN---")] + [ft.dropdownm2.Option(grau.upper()) for grau in self.filtres_globals_fp.graus]   
        )
        self.drop_grau_fp.on_change=lambda _: self.actualitzar_dropdown_cicles_fp()

        self.drop_cicles_fp = ft.DropdownM2(
            label="Cicle",
            hint_text="Cicle",
            expand=True,
            options=[ft.dropdownm2.Option(key="---NINGÚN---", text="---NINGÚN---")] + [
                ft.dropdownm2.Option(key=str(cicle.nom), text=cicle.nom) for cicle in self.cicles_globals_fp
            ]
        )

        # Controls per a canviar de pàgina si hi ha més d'una
        self.fp_inici_page_btn = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE, 
            icon_size=40,
            tooltip="Primera pàgina"
        )
        self.fp_inici_page_btn.on_click=lambda e: asyncio.create_task(self.change_page(e, 1))

        self.fp_before_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS, 
            icon_size=26,
            tooltip="Anterior"
        )
        self.fp_before_btn.on_click=lambda e: asyncio.create_task(self.before_page(e))

        self.fp_next_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD_IOS, 
            icon_size=26,
            tooltip="Següent"
        )
        self.fp_next_btn.on_click=lambda e: asyncio.create_task(self.next_page(e))

        self.fp_num_pagina = ft.TextField(
            value="1", # Valor inicial
            text_size=24,              
            width=60,               # Amplada fixa perquè només és un número
            text_align="center",    # Número centrat
            border_radius=10,
            filled=True,
            border_color="blue-800",
            content_padding=5
        )
        self.fp_num_pagina.on_submit=lambda e: asyncio.create_task(self.change_page(e, self.fp_num_pagina.value))

        self.fp_final_page_btn = ft.IconButton(
        icon=ft.Icons.LAST_PAGE, 
        icon_size=40,
        tooltip="Última pàgina"
        )
        self.fp_final_page_btn.on_click=lambda e: asyncio.create_task(self.change_page(e, self.total_pages_fp))
        self.fp_nav_row = ft.Row([self.fp_inici_page_btn, self.fp_before_btn, self.fp_num_pagina, self.fp_next_btn, self.fp_final_page_btn], alignment="center")

        # --- DEFINICIÓ DROPDOWNS CE ---
        self.drop_provincia_ce = ft.DropdownM2(
            label="Província",
            hint_text="Provincia",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(prov.upper()) for prov in self.filtres_globals_ce.provincies]
        )
        self.drop_provincia_ce.on_change=lambda e: self.actualitzar_comarques(e, cicle_fp=False)

        self.drop_comarca_ce = ft.DropdownM2(
            label="Comarca",
            hint_text="Comarca",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(comarca) for comarca in self.filtres_globals_ce.comarques]
        )
        self.drop_comarca_ce.on_change=lambda e: self.actualitzar_localitats(e, cicle_fp=False)

        self.drop_localitat_ce = ft.DropdownM2(
            label="Localitat",
            hint_text="Localitat",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(localitat) for localitat in self.filtres_globals_ce.localitats]
        )
        self.drop_familia_ce = ft.DropdownM2(
            label="Familia",
            hint_text="Familia",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGUNA---")] + [ft.dropdownm2.Option(familia) for familia in self.filtres_globals_ce.families]
        )
        self.drop_familia_ce.on_change=lambda _: self.actualitzar_dropdown_cursos_ce()

        self.drop_grau_ce = ft.DropdownM2(
            label="Grau",
            hint_text="Grau",
            expand=True,
            options=[ft.dropdownm2.Option("---NINGÚN---")] + [ft.dropdownm2.Option(grau.upper()) for grau in self.filtres_globals_ce.graus]
        )
        self.drop_grau_ce.on_change=lambda _: self.actualitzar_dropdown_cursos_ce()

        self.drop_cursos_ce = ft.DropdownM2(
            label="Curs",
            hint_text="Curs",
            expand=True,
            options=[ft.dropdownm2.Option(key="---NINGÚN---", text="---NINGÚN---")] + [
                ft.dropdownm2.Option(key=str(cicle.nom), text=cicle.nom) for cicle in self.cicles_globals_ce
            ]
        )

        # Controls per a canviar de pàgina si hi ha més d'una
        self.ce_inici_page_btn = ft.IconButton(
            icon=ft.Icons.FIRST_PAGE, 
            icon_size=40,
            tooltip="Primera pàgina"
        )
        self.ce_inici_page_btn.on_click=lambda e: asyncio.create_task(self.change_page(e, 1))

        self.ce_before_btn = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS, 
            icon_size=26,
            tooltip="Anterior"
        )
        self.ce_before_btn.on_click=lambda e: asyncio.create_task(self.before_page(e))

        self.ce_next_btn = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD_IOS, 
            icon_size=26,
            tooltip="Següent"
        )
        self.ce_next_btn.on_click=lambda e: asyncio.create_task(self.next_page(e))

        self.ce_num_pagina = ft.TextField(
            value="1",              # Valor inicial
            text_size=24,
            width=60,               # Amplada fixa perquè només és un número
            text_align="center",    # Número centrat
            border_radius=10,
            filled=True,
            border_color="blue-800",
            content_padding=5
        )
        self.ce_num_pagina.on_submit=lambda e: asyncio.create_task(self.change_page(e, self.ce_num_pagina.value))

        self.ce_final_page_btn = ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            icon_size=40, 
            tooltip="Última pàgina"
        )
        self.ce_final_page_btn.on_click=lambda e: asyncio.create_task(self.change_page(e, self.total_pages_ce))

        self.ce_nav_row = ft.Row([self.ce_inici_page_btn, self.ce_before_btn, self.ce_num_pagina, self.ce_next_btn, self.ce_final_page_btn], alignment="center")


        # --- CONFIGURACIÓ DELS MAPES ---
        # Mapa independent per a FP
        self.map_fp = ftm.Map(
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

        # Mapa independent per a CE
        self.map_ce = ftm.Map(
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

        # --- VISTA 1: CICLES FP ---
        self.vista_cicles = ft.Column([
            ft.Text("CATÀLEG D'OFERTA FORMATIVA CV", size=24, weight="bold", color="blue-800"),
            ft.Divider(height=1, color="grey-300"),
            ft.Row([
                ft.Column([
                    # Contenidor de informació
                    ft.Container(
                        padding=20, bgcolor=ft.Colors.BLUE_GREY_100, border_radius=15,
                        content=ft.Column([
                            ft.Row([
                                self.drop_provincia_fp, 
                                self.drop_comarca_fp, 
                                self.drop_localitat_fp
                                ], spacing=10),
                            ft.Row([
                                self.drop_familia_fp, 
                                self.drop_grau_fp, 
                                self.drop_cicles_fp
                            ], spacing=10),
                            ft.Row([
                                ft.Button("BUSCAR",
                                                data="search_button", 
                                                icon=ft.Icons.SEARCH, 
                                                style=ft.ButtonStyle(
                                                    bgcolor="#076350",
                                                    color=ft.Colors.WHITE,
                                                    padding=10), 
                                                on_click=lambda e: asyncio.create_task(self.handle_search(e, cicle_fp=True)), 
                                                tooltip="Buscar resultats"),
                                ft.Button("NETEJAR",
                                                data="clean_button", 
                                                icon=ft.Icons.REFRESH, 
                                                style=ft.ButtonStyle(
                                                    bgcolor="#076350",
                                                    color=ft.Colors.WHITE,
                                                    padding=10), 
                                                on_click=lambda e: asyncio.create_task(self.refresh_dropdowns(e, cicle_fp=True)), 
                                                tooltip="Netejar la finestra")
                                                  ], alignment=ft.MainAxisAlignment.CENTER)
                        ])
                    ),
                    # Número de resultats
                    ft.Container(content=ft.Row([self.fp_result_text, self.fp_nav_row], spacing=190)),
                    # Contenidor de resultats (Targetes)
                    ft.Container(content=self.results_col_fp, width=450, expand=True, alignment=ft.Alignment.TOP_LEFT)
                ], expand=True, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                ft.VerticalDivider(width=1, color=ft.Colors.BLUE_100),
                # Contenidor del Mapa
                ft.Container(ref=self.map_container_fp, expand=True, border=ft.Border.all(1, ft.Colors.BLUE_GREY_200), border_radius=15, content=self.map_fp)
                ], expand=True)
        ], expand=True)

        # --- VISTA 2: CURSOS ESPECIALITZACIÓ ---
        self.vista_especialitzacio = ft.Column([
            ft.Text("CATÀLEG D'OFERTA FORMATIVA CV", size=24, weight="bold", color="blue-800"),
            ft.Divider(height=1, color="grey-300"),
            ft.Row([
                ft.Column([
                    # Contenidor de informació (Filtres)
                    ft.Container(
                        padding=20, bgcolor=ft.Colors.BLUE_GREY_100, border_radius=15,
                        content=ft.Column([
                            ft.Row([
                                self.drop_provincia_ce, 
                                self.drop_comarca_ce, 
                                self.drop_localitat_ce
                            ], spacing=10),
                            ft.Row([
                                self.drop_familia_ce, 
                                self.drop_grau_ce, 
                                self.drop_cursos_ce
                            ], spacing=10),
                            ft.Row([
                                ft.Button("BUSCAR", 
                                                data="search_button",
                                                icon=ft.Icons.SEARCH, 
                                                style=ft.ButtonStyle(
                                                    bgcolor="#076350",
                                                    color=ft.Colors.WHITE,
                                                    padding=10), 
                                                on_click=lambda e: asyncio.create_task(self.handle_search(e, cicle_fp=False)), 
                                                tooltip="Buscar resultats"),
                                ft.Button("NETEJAR", 
                                                data="clean_button",
                                                icon=ft.Icons.REFRESH, 
                                                style=ft.ButtonStyle(
                                                    bgcolor="#076350",
                                                    color=ft.Colors.WHITE,
                                                    padding=10), 
                                                on_click=lambda e: asyncio.create_task(self.refresh_dropdowns(e, cicle_fp=True)), 
                                                tooltip="Netejar la finestra")
                            ], alignment=ft.MainAxisAlignment.CENTER)
                        ])
                    ),
                    # Número de resultats 
                    ft.Container(content=ft.Row([self.ce_result_text, self.ce_nav_row], spacing=190)),
                    # Contenidor de resultats (Targetes)
                    ft.Container(
                        content=self.results_col_ce, 
                        width=450, 
                        expand=True, 
                        alignment=ft.Alignment.TOP_LEFT
                    )
                ], expand=True, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                
                ft.VerticalDivider(width=1, color=ft.Colors.BLUE_100),
                
                # Contenidor del Mapa
                ft.Container(
                    ref=self.map_container_ce, 
                    expand=True, 
                    border=ft.Border.all(1, ft.Colors.BLUE_GREY_200), 
                    border_radius=15, 
                    content=self.map_ce
                )
            ], expand=True)
        ], expand=True)

        # --- VISTA 3: CHATBOT IA ---
        self.chat_history = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
        self.chat_input = ft.TextField(hint_text="Pregunta sobre itineraris, eixides o cicles...", expand=True, on_submit=self.enviar_missatge_chat)
        
        

        # --- TABS I CONTENIDOR PRINCIPAL ---
        # Contenidor que mostrarà el contingut de la pestanya activa
        self.main_content_area = ft.Column([self.vista_cicles], expand=True)

        self.tabs = ft.Tabs(
            selected_index=0,
            length=3,
            animation_duration=300,
            content=ft.Column(              
                expand=True,              
                controls=[ft.TabBar(                
                    tabs=[
                        ft.Tab(label="Cicles FP", icon=ft.Icons.SCHOOL),
                        ft.Tab(label="Especialització", icon=ft.Icons.WORKSPACE_PREMIUM),
                        ft.Tab(label="Assistent IA", icon=ft.Icons.AUTO_AWESOME)
                    ]
                )]
            ),
        )
        self.tabs.on_change = self.canviar_pestanya

        # Inicialitzem amb la primera pestanya
        self.main_content_area.controls.clear()
        self.main_content_area.controls.append(self.vista_cicles)

        # Afegim tot a la pàgina
        self.page.add(
            ft.Column([
                self.tabs,
                ft.Divider(height=1),
                self.main_content_area
            ], expand=True)
        )
        self.page.update()

    
    # Funció per al canvi de pestanyes
    def canviar_pestanya(self, e):
        idx = self.tabs.selected_index

        self.main_content_area.controls.clear()

        if idx == 0:
            self.main_content_area.controls.append(self.vista_cicles)
        elif idx == 1:
            self.main_content_area.controls.append(self.vista_especialitzacio)
        elif idx == 2:
            self.main_content_area.controls.append(self.vista_chatbot)

        self.page.update()
    
    # FUNCIONS PER AL CANVI DE PÀGINA DE RESULTATS
    # Funció per canviar de pàgina introduint el número de pàgina
    async def change_page(self, e, num_pagina):
        num_pagina=int(num_pagina)
        cicle_fp = True
        if self.tabs.selected_index == 0:
            if num_pagina < 1:
                num_pagina = 1
            elif num_pagina > self.total_pages_fp:
                num_pagina = self.total_pages_fp
            self.num_pagina_actual_fp = num_pagina
        else:
            cicle_fp = False
            if num_pagina < 1:
                num_pagina = 1
            elif num_pagina > self.total_pages_ce:
                num_pagina = self.total_pages_ce
            self.num_pagina_actual_ce = num_pagina
        await self.handle_search(e, cicle_fp)

    # Funció per passar a la pàgina següent
    async def next_page(self, e):
        cicle_fp = True
        if self.tabs.selected_index == 0:
            if self.num_pagina_actual_fp <= self.total_pages_fp:
                self.num_pagina_actual_fp += 1
        elif self.tabs.selected_index == 1:
            cicle_fp = False
            if self.num_pagina_actual_ce <= self.total_pages_ce:
                self.num_pagina_actual_ce += 1
        await self.handle_search(e, cicle_fp)

    # Funció per passar a la pàgina anterior
    async def before_page(self, e):
        cicle_fp = True
        if self.tabs.selected_index == 0:
            if self.num_pagina_actual_fp > 1: self.num_pagina_actual_fp -= 1
        else:
            cicle_fp = False
            if self.num_pagina_actual_ce > 1: self.num_pagina_actual_ce -= 1
        await self.handle_search(e, cicle_fp)

    # Funció per enviar el input del usuari en el chatbot
    def enviar_missatge_chat(self, e):
        if not self.chat_input.value: return
        # Afegeix el missatge de l'usuari
        self.chat_history.controls.append(
            ft.Text(f"Usuari: {self.chat_input.value}", weight="bold", color=ft.Colors.BLUE_800)
        )
        self.chat_input.value = ""
        self.page.update()
    
    # Funció per netejar la informació dels Dropdowns
    async def refresh_dropdowns(self, e, cicle_fp=True):
        if cicle_fp:
            self.drop_provincia_fp.value = "---NINGUNA---"
            self.drop_comarca_fp.value = "---NINGUNA---"
            self.drop_localitat_fp.value = "---NINGUNA---"
            self.drop_familia_fp.value = "---NINGUNA---"
            self.drop_grau_fp.value = "---NINGÚN---"
            self.drop_cicles_fp.value = "---NINGÚN---"

            self.results_col_fp.controls.clear()
            self.fp_result_text.value = "0 resultats"

            await self.actualitzar_mapa_centre()
        else:
            self.drop_provincia_ce.value = "---NINGUNA---"
            self.drop_comarca_ce.value = "---NINGUNA---"
            self.drop_localitat_ce.value = "---NINGUNA---"
            self.drop_familia_ce.value = "---NINGUNA---"
            self.drop_grau_ce.value = "---NINGÚN---"
            self.drop_cursos_ce.value = "---NINGÚN---"

            self.results_col_ce.controls.clear()
            self.ce_result_text.value = "0 resultats"

            await self.actualitzar_mapa_centre(cicle_fp=False)

        self.page.update()

    # LÒGICA DE FILTRES DEPENDENTS
    # Funció per actualitzar la informació de les comarques depenent de la província escollida
    def actualitzar_comarques(self, e, cicle_fp=True):
        if cicle_fp:
            prov_triada = self.drop_provincia_fp.value

            noves_comarques = obtenir_comarques(prov_triada)
            
            self.drop_comarca_fp.options = [ft.dropdownm2.Option("---NINGUNA---")]
            for comarca in noves_comarques:
                self.drop_comarca_fp.options.append(ft.dropdownm2.Option(comarca.upper()))
            
            self.drop_comarca_fp.value = "---NINGUNA---"
            self.actualitzar_localitats(e)
            self.actualitzar_dropdown_cicles_fp()
        else:
            prov_triada = self.drop_provincia_ce.value

            noves_comarques = obtenir_comarques(prov_triada)
            
            self.drop_comarca_ce.options = [ft.dropdownm2.Option("---NINGUNA---")]
            for comarca in noves_comarques:
                self.drop_comarca_ce.options.append(ft.dropdownm2.Option(comarca.upper()))
            
            self.drop_comarca_ce.value = "---NINGUNA---"
            self.actualitzar_localitats(e, cicle_fp)
            self.actualitzar_dropdown_cursos_ce()

    # Funció per actualitzar la informació de les localitats depenent de la província i/o comarca escollida
    def actualitzar_localitats(self, e, cicle_fp=True):
        # Lògica per als cicles de FP
        if cicle_fp:
            comarca_sel = self.drop_comarca_fp.value
            provincia_sel = self.drop_provincia_fp.value
            
            # Cap filtre seleccionat (Tot a "NINGUNA")
            if comarca_sel == "---NINGUNA---" and provincia_sel == "---NINGUNA---":
                noves_localitats = self.filtres_globals_fp.localitats
                
            # Només tenim la Província (Comarca és "NINGUNA")
            elif comarca_sel == "---NINGUNA---":
                noves_localitats = obtenir_localitats_de_provincia(provincia_sel)
                
            # Tenim una Comarca específica
            else:
                noves_localitats = obtenir_localitats_de_comarca(comarca_sel)

            # Actualització visual
            self.drop_localitat_fp.options = [ft.dropdownm2.Option("---NINGUNA---")]
            for localitat in noves_localitats:
                self.drop_localitat_fp.options.append(ft.dropdownm2.Option(localitat.upper()))
            
            self.drop_localitat_fp.value = "---NINGUNA---"
            self.actualitzar_dropdown_cicles_fp()
        
        # Lògica per als cursos d'especialització
        else:
            comarca_sel = self.drop_comarca_ce.value
            provincia_sel = self.drop_provincia_ce.value
            
            # Cap filtre seleccionat (Tot a "NINGUNA")
            if comarca_sel == "---NINGUNA---" and provincia_sel == "---NINGUNA---":
                noves_localitats = self.filtres_globals_ce.localitats
                
            # Només tenim la Província (Comarca és "NINGUNA")
            elif comarca_sel == "---NINGUNA---":
                noves_localitats = obtenir_localitats_de_provincia(provincia_sel)
                
            # Tenim una Comarca específica
            else:
                noves_localitats = obtenir_localitats_de_comarca(comarca_sel)

            # Actualització visual
            self.drop_localitat_ce.options = [ft.dropdownm2.Option("---NINGUNA---")]
            for localitat in noves_localitats:
                self.drop_localitat_ce.options.append(ft.dropdownm2.Option(localitat.upper()))
            
            self.drop_localitat_ce.value = "---NINGUNA---"
            self.actualitzar_dropdown_cursos_ce()
    
    # Funció per actualitzar la informació dels Dropdown de FP
    def actualitzar_dropdown_cicles_fp(self):
        # Recollim tots els estats actuals
        params = {
            "provincia": self.drop_provincia_fp.value if self.drop_provincia_fp.value != "---NINGUNA---" else None,
            "comarca": self.drop_comarca_fp.value if self.drop_comarca_fp.value != "---NINGUNA---" else None,
            "localitat": self.drop_localitat_fp.value if self.drop_localitat_fp.value != "---NINGUNA---" else None,
            "familia": self.drop_familia_fp.value if self.drop_familia_fp.value != "---NINGUNA---" else None,
            "grau": self.drop_grau_fp.value if self.drop_grau_fp.value != "---NINGÚN---" else None
        }


        # Retorna una llista d'objectes Cicle
        nous_cicles = obtenir_cicles_filtrats(params["provincia"], params["comarca"], params["localitat"], params["familia"], params["grau"])

        # Actualitza les opcions del Dropdown
        self.drop_cicles_fp.options = [ft.dropdownm2.Option(key="---NINGÚN---", text="---NINGÚN---")]
        for cicle in nous_cicles:
            self.drop_cicles_fp.options.append(ft.dropdownm2.Option(key=str(cicle.nom.upper()), text=cicle.nom.upper()))
        
        self.drop_cicles_fp.value = "---NINGÚN---"
        self.page.update()
    
    # Funció per actualitzar la informació dels Dropdown de CE
    def actualitzar_dropdown_cursos_ce(self):
        # Recollim tots els estats actuals
        params = {
            "provincia": self.drop_provincia_ce.value if self.drop_provincia_ce.value != "---NINGUNA---" else None,
            "comarca": self.drop_comarca_ce.value if self.drop_comarca_ce.value != "---NINGUNA---" else None,
            "localitat": self.drop_localitat_ce.value if self.drop_localitat_ce.value != "---NINGUNA---" else None,
            "familia": self.drop_familia_ce.value if self.drop_familia_ce.value != "---NINGUNA---" else None,
            "grau": self.drop_grau_ce.value if self.drop_grau_ce.value != "---NINGÚN---" else None
        }


        # Retorna una llista d'objectes Cicle
        nous_cursos = obtenir_cursos_filtrats(params["provincia"], params["comarca"], params["localitat"], params["familia"], params["grau"])

        # Actualitza les opcions del Dropdown
        self.drop_cursos_ce.options = [ft.dropdownm2.Option(key="---NINGÚN---", text="---NINGÚN---")]
        for cicle in nous_cursos:
            self.drop_cursos_ce.options.append(ft.dropdownm2.Option(key=str(cicle.nom.upper()), text=cicle.nom.upper()))
        
        self.drop_cursos_ce.value = "---NINGÚN---"
        self.page.update()

    # --- GESTIÓ DE CERCA I TARGETES ---
    async def handle_search(self, e, cicle_fp=True):
        # Gestionar el reinici de la paginació
        if e.control and e.control.data == "search_button":
            if cicle_fp:
                self.num_pagina_actual_fp = 1
            else:
                self.num_pagina_actual_ce = 1

        pag = self.num_pagina_actual_fp if cicle_fp else self.num_pagina_actual_ce

        # LÒGICA PER A CICLES DE FP (FP)
        if cicle_fp:
            self.fp_num_pagina.value = str(pag)
            self.results_col_fp.controls.clear()
            self.lat_lon_fplist.clear()

            nom_cicle = self.drop_cicles_fp.value if self.drop_cicles_fp.value != "---NINGÚN---" else None
            if self.drop_grau_fp.value == 'BÁSICO 2A OPORT.':
                self.drop_grau_fp.value = 'BÁSICO 2a Oport.'
            
            cicle_id = None
            if nom_cicle and nom_cicle != "---NINGÚN---":
                # Busquem l'objecte cicle que té eixe nom exactament
                cicle_trobat = next((c for c in self.cicles_globals_fp if c.nom == nom_cicle), None)
                if cicle_trobat:
                    cicle_id = cicle_trobat.id

            # crida al controlador (retorna un diccionari)
            resposta = executar_cerca_oferta(
                tipus="FP",
                pagina=pag,
                provincia=self.drop_provincia_fp.value if self.drop_provincia_fp.value != "---NINGUNA---" else None,
                comarca=self.drop_comarca_fp.value if self.drop_comarca_fp.value != "---NINGUNA---" else None,
                localitat=self.drop_localitat_fp.value if self.drop_localitat_fp.value != "---NINGUNA---" else None,
                familia=self.drop_familia_fp.value if self.drop_familia_fp.value != "---NINGUNA---" else None,
                grau=self.drop_grau_fp.value if self.drop_grau_fp.value != "---NINGÚN---" else None,
                id_cicle=cicle_id
            )

            # Accés a les dades del diccionari
            oferta = resposta.get("oferta", [])
            self.total_res_fp = resposta.get("total", 0)
            self.total_pages_fp = resposta.get("pagines_totals", 1)

            # Actualitzem el comptador i estat dels botons
            self.fp_result_text.value = f"{self.total_res_fp} resultats"
            self.fp_before_btn.disabled = (pag <= 1)
            self.fp_next_btn.disabled = (pag >= self.total_pages_fp)

            for result in oferta:
                card = self.vista_chatbot.create_card(
                    result, 
                    on_map_click=lambda c, _: self.actualitzar_mapa_centre(c, cicle_fp=True),
                    tipus_vista="fp"
                )
                if result.latitud and result.longitud:
                    self.lat_lon_fplist.append((result.latitud, result.longitud))
                self.results_col_fp.controls.append(card)
            
            if self.lat_lon_fplist:
                await self.vista_chatbot.generar_mapa_multiple(self.lat_lon_fplist, tipus_vista="fp", multiple_coords=True)

        # LÒGICA PER A CURSOS D'ESPECIALITZACIÓ (CE)
        else:
            
            self.ce_num_pagina.value = str(pag)
            self.results_col_ce.controls.clear()
            self.lat_lon_celist.clear()

            nom_curs = self.drop_cursos_ce.value if self.drop_cursos_ce.value != "---NINGÚN---" else None
            cicle_id = None
            if nom_curs and nom_curs != "---NINGÚN---":
                # Busquem l'objecte cicle que té eixe nom exactament
                curs_trobat = next((c for c in self.cicles_globals_ce if c.nom == nom_curs), None)
                if curs_trobat:
                    cicle_id = curs_trobat.id
            
            resposta = executar_cerca_oferta(
                tipus="CE",
                pagina=pag,
                provincia=self.drop_provincia_ce.value if self.drop_provincia_ce.value != "---NINGUNA---" else None,
                comarca=self.drop_comarca_ce.value if self.drop_comarca_ce.value != "---NINGUNA---" else None,
                localitat=self.drop_localitat_ce.value if self.drop_localitat_ce.value != "---NINGUNA---" else None,
                familia=self.drop_familia_ce.value if self.drop_familia_ce.value != "---NINGUNA---" else None,
                grau=self.drop_grau_ce.value if self.drop_grau_ce.value != "---NINGÚN---" else None,
                id_cicle=cicle_id
            )

            oferta = resposta.get("oferta", [])
            self.total_res_ce = resposta.get("total", 0)
            self.total_pages_ce = resposta.get("pagines_totals", 1)

            self.ce_result_text.value = f"{self.total_res_ce} resultats"
            self.ce_before_btn.disabled = (pag <= 1)
            self.ce_next_btn.disabled = (pag >= self.total_pages_ce)

            for result in oferta:
                card = self.vista_chatbot.create_card(
                    result, 
                    on_map_click=lambda c, _: self.actualitzar_mapa_centre(c, cicle_fp=False),
                    tipus_vista="ce"
                )
                if result.latitud and result.longitud:
                    self.lat_lon_celist.append((result.latitud, result.longitud))
                self.results_col_ce.controls.append(card)
            
            if self.lat_lon_celist:
                await self.vista_chatbot.generar_mapa_multiple(self.lat_lon_celist, tipus_vista="ce", multiple_coords=True)
        self.page.update()

    # Lògica per ubicar un centre amb un punt en el mapa
    # o tota la comunitat Valenciana en cas de no passar-li cap centre
    async def actualitzar_mapa_centre(self, centre=None, cicle_fp=True):
        if centre and centre.latitud and centre.longitud:
            coords = [(float(centre.latitud), float(centre.longitud))]
            if cicle_fp:
                self.lat_lon_fplist = coords
            else:
                self.lat_lon_celist = coords
        # Generem mapa amb les coordenades actuals
        await self.vista_chatbot.generar_mapa_multiple(
            self.lat_lon_fplist if cicle_fp else self.lat_lon_celist,
            tipus_vista="fp" if cicle_fp else "ce"
        )
        self.page.update()


if __name__ == "__main__":
    ft.run(FpApp, view=ft.AppView.WEB_BROWSER)