import flet as ft


class SideMenu(ft.Container):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        super().__init__()
        self.app_page = page
        self.lang = lang
        self.user_state = user_state

        self.width = self.get_menu_width()
        self.left = -self.width
        self.top = 0
        self.bottom = 0
        self.bgcolor = ft.Colors.BLUE_GREY_900
        self.padding = 20
        self.animate_position = ft.Animation(300, ft.AnimationCurve.EASE_OUT)

        self.menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            icon_color=ft.Colors.GREEN,
            icon_size=40,
            on_click=self.open_menu
        )

        def navigate_to(route):
            async def handler(e):
                await self.app_page.push_route(route)

            return handler

        self.content = ft.Column([
            ft.Row([
                ft.Text(self.lang["generic.menu"], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.IconButton(icon=ft.Icons.CLOSE, icon_color=ft.Colors.WHITE, on_click=self.close_menu)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(
                content=ft.Text(self.lang["generic.home"], color=ft.Colors.WHITE, size=20),
                on_click=navigate_to("/home"),
            ),
            ft.Container(
                content=ft.Text(self.lang["generic.lesson"], color=ft.Colors.WHITE, size=20),
                on_click=navigate_to("/lessons"),
            ),
            ft.Text(self.lang["generic.practice"], color=ft.Colors.WHITE, size=20),
            ft.Text(self.lang["generic.test"], color=ft.Colors.WHITE, size=20),
            ft.Container(
                content=ft.Text(self.lang["generic.saving"], color=ft.Colors.WHITE, size=20),
                on_click=navigate_to("/saving"),
            ),
            ft.Text(self.lang["generic.spending"], color=ft.Colors.WHITE, size=20),
            ft.Text(self.lang["generic.character"], color=ft.Colors.WHITE, size=20),
            ft.Text(self.lang["generic.shop"], color=ft.Colors.WHITE, size=20),
            ft.Container(
                content=ft.Text(self.lang["generic.change_user"], color=ft.Colors.WHITE, size=20),
                on_click=self.change_user,
            ),
            #ft.Container(
            #    content=ft.Text("temp", color=ft.Colors.WHITE, size=20),
            #    on_click=navigate_to("/add_saving"),
            #)
        ])

    def get_menu_width(self) -> int:
        current_width = self.app_page.window.width if hasattr(self.app_page, 'window') else self.app_page.width
        if current_width >= 650:
            return 250
        elif current_width >= 260:
            return int(current_width // 2.6)
        else:
            return 100

    def open_menu(self, e=None) -> None:
        self.width = self.get_menu_width()
        self.left = 0
        self.update()

    def close_menu(self, e=None) -> None:
        self.left = -self.get_menu_width()
        self.update()


    async def change_user(self, e=None) -> None:
        self.user_state["current_user"] = None
        await self.app_page.push_route("/login")
