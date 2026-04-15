import flet as ft
from src.pages.global_elements.menu import SideMenu

def get_lessons_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    menu = SideMenu(page, lang, user_state)
    menu_button = menu.menu_button

    search_bar = ft.TextField(
        hint_text=lang["lessons.search"],
        color=ft.Colors.GREY_900,
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        filled=True,
        bgcolor=ft.Colors.GREY_50,
        border_color=ft.Colors.TRANSPARENT,
        height=40,
        expand=True,
        content_padding=10,
        text_size=14
    )

    top_nav_bar = ft.Row(
        controls=[
            ft.Container(content=menu_button, alignment=ft.Alignment.CENTER),
            search_bar,
            #ft.IconButton(icon=ft.Icons.SETTINGS, icon_color=ft.Colors.GREY_500),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    header_text = ft.Column(
        spacing=5,
        controls=[
            ft.Text(lang["lessons.title"], size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
            #ft.Text(lang["lessons.description"], size=14, color=ft.Colors.GREY_600)
        ]
    )

    milestone_card = ft.Container(
        expand=2,
        bgcolor="#287b35",
        border_radius=15,
        height=200,
        padding=20,
        content=ft.Column(
            spacing=15,
            controls=[
                #ft.Container(
                #    content=ft.Text("CURRENT MILESTONE", size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                #    bgcolor=""#4a9554",
                #    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                #    border_radius=20
                #),
                ft.Text(lang["lessons.previous_lesson_head"], size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text(lang["lessons.previous_lesson"], size=13, color=ft.Colors.WHITE_70),
                ft.Container(height=10),
                ft.Column(
                    spacing=5,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.Text(lang["lessons.overall_completion"], size=12, color=ft.Colors.BLACK_87),
                                ft.Row(
                                    [
                                        ft.Text("18%", size=12, color=ft.Colors.WHITE),
                                        ft.Container(width=20),
                                        ft.Text("Lvl ?", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                                )
                            ]
                        ),
                        ft.ProgressBar(value=0.18, color=ft.Colors.WHITE, bgcolor=ft.Colors.WHITE_30, height=6)
                    ]
                )
            ]
        )
    )

    stats_card = ft.Container(
        expand=1,
        bgcolor="#E8F0E6",
        border_radius=15,
        height=200,
        padding=15,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=25,
            controls=[
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.TIMER, color=ft.Colors.BLUE_800, size=20),
                            bgcolor="#D1E4FA", padding=10, border_radius=10
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(lang["lessons.learning_time"], size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                                ft.Text(f"$hour {lang["generic.hours"]}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
                            ]
                        )
                    ]
                ),
                ft.Row(
                    spacing=15,
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.VERIFIED, color=ft.Colors.GREEN_800, size=20),
                            bgcolor="#CDE5D0", padding=10, border_radius=10
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(lang["lessons.certificates"], size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                                ft.Text("0", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
                            ]
                        )
                    ]
                )
            ]
        )
    )

    dashboard_row = ft.Row(spacing=20, controls=[milestone_card, stats_card])

    categories = [lang["lessons.cat_all"]]
    tabs_row = ft.Row(
        spacing=10,
        controls=[
            ft.Container(
                content=ft.Text(cat, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE if cat == "All" else ft.Colors.BLUE_GREY_600),
                bgcolor=ft.Colors.GREEN_800 if cat == "All" else ft.Colors.GREY_200,
                padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                border_radius=20,
            ) for cat in categories
        ]
    )

    center_container = ft.Container(
        content=ft.Column(
            spacing=25,
            controls=[
                top_nav_bar,
                header_text,
                dashboard_row,
                tabs_row
            ]
        ),
        padding=20,
        width=650
    )

    page_content = ft.Container(
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[center_container]
                )
            ]
        ),
        expand=True,
        padding=0
    )

    def on_page_resize(e) -> None:
        current_width = page.width if e is None else e.width
        if not current_width: current_width = 650
        safe_width = min(current_width, 650)
        try:
            center_container.width = safe_width
            page.update()
        except Exception:
            pass

    page.on_resize = on_page_resize
    on_page_resize(None)

    return ft.View(
        route="/lessons",
        padding=0,
        bgcolor="#FAFAF8",
        controls=[
            ft.Stack(
                controls=[page_content, menu],
                expand=True
            )
        ]
    )