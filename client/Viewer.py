import flet as ft
from TravelClient import TravelClient
from time import sleep

client = TravelClient()

def main(page: ft.Page):
    page.title = "Tela de Login"
    page.window_width = 800
    page.window_height = 600
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    pageRouter = 'login'
    user_name = ""
    status_text = ft.Text("")
    travelsList = []

    def window_event(e):
        if e.data == "close":
            on_close(e)
            page.window.destroy()
            page.update()
    page.window.prevent_close = True
    page.window.on_event = window_event 

    def login(e):
        username = username_field.value
        password = password_field.value

        client.login(username, password)

        if client.session_token:
            nonlocal user_name
            user_name = username 
            status_text.value = "Login realizado com sucesso!"
            status_text.color = ft.colors.GREEN
            sleep(1)
            navigate_to_menu(e)
        else:
            status_text.value = "Credenciais inválidas!"
            status_text.color = ft.colors.RED

        update_page()

    def on_register(e):
        username = username_field.value
        name = name_input.value
        password = password_field.value
        client.register(username, name, password)
        if client.session_token:
            nonlocal user_name
            user_name = name
            status_text.value = "Cadastro realizado com sucesso!"
            status_text.color = ft.colors.GREEN
            sleep(1)
            navigate_to_menu(e)
        else:
            status_text.value = "Erro ao realizar cadastro!"
            status_text.color = ft.colors.RED

        update_page()

    def navigate_to_register(e):
        username_field.value = ''
        password_field.value = ''
        name_input.value = ''
        nonlocal pageRouter
        pageRouter = 'register'
        update_page()

    def navigate_to_login(e):
        username_field.value = ''
        password_field.value = ''
        name_input.value = ''
        nonlocal pageRouter
        pageRouter = 'login'
        update_page()

    def navigate_to_menu(e):
        nonlocal pageRouter
        pageRouter = 'menu'
        client.list_travels()
        travel_containers = []
        travels = client.list
        for travel in travels:
            origin, destination = travel
            travel_containers.append(
                ft.Container(
                    alignment=ft.alignment.center,
                    width=100,
                    height=100,
                    bgcolor=ft.colors.AMBER,
                    border_radius=ft.border_radius.all(5),
                    expand=True,
                    content=ft.Text('dewdwe'),
                )
            )
        nonlocal travelsList
        travelsList = ft.Column(
            wrap=True,
            spacing=10,
            run_spacing=10,
            controls=travel_containers,
        )
        print(travelsList)
        update_page()

    def on_close(e):
        client.close()
    
    def items(count):
        items = []
        for i in range(1, count + 1):
            items.append(
                ft.Container(
                    content=ft.Text(value=str(i)),
                    alignment=ft.alignment.center,
                    width=100,
                    height=100,
                    bgcolor=ft.colors.AMBER,
                    border_radius=ft.border_radius.all(5),
                )
            )
        return items

    def get_travels():
        travel_containers = []
        if(client.list != {}):
            travels = client.list
            for travel in travels:
                origin, destination = travel
                travel_containers.append(
                    ft.Container(
                        alignment=ft.alignment.center,
                        width=100,
                        height=100,
                        bgcolor=ft.colors.AMBER,
                        border_radius=ft.border_radius.all(5),
                        expand=True,
                        content=ft.Column(
                            controls=[
                                ft.Text(f"Origem: {origin}", size=16, weight=ft.FontWeight.BOLD),
                                ft.Text(f"Destino: {destination}", size=14),
                            ],
                        ),
                    )
                )
        return travel_containers

    title = ft.Text("Login", size=30, weight=ft.FontWeight.BOLD)

    name_input = ft.TextField(label="Nome", width=250)
    username_field = ft.TextField(label="Usuário", width=250)
    password_field = ft.TextField(label="Senha", password=True, width=250)

    register_button = ft.TextButton(text="Cadastrar", width=300, scale=0.8, on_click=on_register)
    login_button = ft.ElevatedButton(text="Entrar", on_click=login, width=250)
    switch_to_register_button = ft.TextButton(text="Cadastrar", on_click=navigate_to_register, width=250)
    switch_to_login_button = ft.TextButton(text="Voltar ao Login", on_click=navigate_to_login, width=250)
    col = ft.Column(
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=items(9),
    )

    def update_page():
        page.controls.clear()
        if pageRouter == 'login':
            page.add(
                ft.Column(
                    controls=[
                        title,
                        username_field,
                        password_field,
                        login_button,
                        switch_to_register_button,
                        status_text
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        elif pageRouter == 'register':
            page.add(
                ft.Column(
                    controls=[
                        ft.Text("Cadastro", size=30, weight=ft.FontWeight.BOLD),
                        name_input,
                        username_field,
                        password_field,
                        register_button,
                        switch_to_login_button,
                        status_text
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                )
            )
        elif pageRouter == 'menu':
            page.add(
                ft.Container(
                    padding=50,
                    expand=1,
                    content=ft.Tabs(
                        animation_duration=300,
                        tabs=[
                            ft.Tab(
                                text="Viagem",
                                icon=ft.icons.AIRPLANE_TICKET,
                                content=ft.Container(
                                    padding=20,
                                    margin=10,
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.WHITE10,
                                    width=150,
                                    height=150,
                                    border_radius=10,
                                    content=travelsList
                                ),
                            ),
                            ft.Tab(
                                text="Passagens Não confirmadas",
                                icon=ft.icons.SHOPPING_CART_CHECKOUT,
                                content=ft.Container(
                                    padding=20,
                                    margin=10,
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.WHITE10,
                                    width=150,
                                    height=150,
                                    border_radius=10,
                                    content=col
                                ),
                            ),
                            ft.Tab(
                                text="Passagens confirmadas",
                                icon=ft.icons.SHOP,
                                content=ft.Container(
                                    padding=20,
                                    margin=10,
                                    alignment=ft.alignment.center,
                                    bgcolor=ft.colors.WHITE10,
                                    width=150,
                                    height=150,
                                    border_radius=10,
                                    content=ft.Card(
                                        content=ft.Text("This is Tab 3"),
                                    )
                                ),
                            ),
                        ],
                    )
                ),
            )
        page.update()

    update_page()

ft.app(target=main)
