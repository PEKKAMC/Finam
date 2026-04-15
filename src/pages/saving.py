import flet as ft
from src.pages.global_elements.menu import SideMenu


def get_savings_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    menu = SideMenu(page, lang, user_state)
    menu_button = menu.menu_button

    top_nav_bar = ft.Row(
        controls=[
            ft.Container(content=menu_button, alignment=ft.Alignment.CENTER),
        ],
        alignment=ft.MainAxisAlignment.START
    )

    goal_title_input = ft.TextField(label=lang["saving.goal_title"])
    goal_amount_input = ft.TextField(label=lang["saving.target_amount"], keyboard_type=ft.KeyboardType.NUMBER)
    reason_input = ft.TextField(label=lang["saving.reason"])

    def close_dlg(e):
        new_objective_dlg.open = False
        page.update()

    def add_objective(e):
        title = goal_title_input.value if goal_title_input.value else lang["saving.untitled_goal"]
        subtitle = reason_input.value if reason_input.value else lang["saving.no_reason"]

        try:
            target_amount = float(goal_amount_input.value)
        except (ValueError, TypeError):
            target_amount = 0.0

        target_str = f"${target_amount:,.0f}"

        new_card = create_objective_card(
            icon_name=ft.Icons.FLAG,
            tag_text="Custom",
            tag_color="#ef6c00",
            tag_bg="#ffe0b2",
            title=title,
            subtitle=subtitle,
            current_val="$0",
            target_val=target_str,
            percentage_str="0%",
            progress_val=0.0,
            bar_color="#ef6c00"
        )

        cards_row.controls.append(new_card)

        goal_title_input.value = ""
        goal_amount_input.value = ""
        reason_input.value = ""

        new_objective_dlg.open = False
        page.update()

    new_objective_dlg = ft.AlertDialog(
        title=ft.Text("+ " + lang["saving.create_objectives"]),
        content=ft.Column(
            tight=True,
            controls=[
                goal_title_input,
                goal_amount_input,
                reason_input,
            ]
        ),
        actions=[
            ft.TextButton(lang["generic.cancel"], on_click=close_dlg),
            ft.Button(lang["saving.save_objective"], on_click=add_objective, bgcolor="#1d7333", color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_new_objective(e):
        if new_objective_dlg not in page.overlay:
            page.overlay.append(new_objective_dlg)

        new_objective_dlg.open = True
        page.update()

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                spacing=5,
                controls=[
                    ft.Text(lang["saving.title"], size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                    ft.Text(
                        lang["saving.description"],
                        size=14, color=ft.Colors.GREY_800
                    )
                ]
            ),
            ft.Button(
                "+ Define New Objective",
                color=ft.Colors.WHITE,
                bgcolor="#1d7333",
                height=45,
                on_click=open_new_objective
            )
        ]
    )

    aggregate_card = ft.Container(
        expand=2,
        bgcolor="#f0f5ee",
        height=200,
        border_radius=12,
        padding=25,
        content=ft.Column(
            spacing=8,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Text(lang["saving.aggregate_portfolio_value"], size=11, weight=ft.FontWeight.BOLD, color="#5a7a5d"),
                ft.Text("$money", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Container(height=15),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(lang["saving.progression"], size=13, color=ft.Colors.BLACK_87),
                        ft.Text("67%", size=13, weight=ft.FontWeight.BOLD, color="#1d7333")
                    ]
                ),
                ft.ProgressBar(value=0.67, color="#2e7d32", bgcolor="#dcedc8", height=8)
            ]
        )
    )

    on_track_card = ft.Container(
        expand=1,
        bgcolor="#145c26",
        height=200,
        border_radius=12,
        padding=25,
        content=ft.Column(
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Container(height=5),
            ]
        )
    )

    dashboard_row = ft.Row(spacing=20, controls=[aggregate_card, on_track_card])

    def create_objective_card(icon_name, tag_text, tag_color, tag_bg, title, subtitle, current_val, target_val, percentage_str, progress_val, bar_color):
        return ft.Container(
            width=260,
            bgcolor=ft.Colors.WHITE,
            border_radius=12,
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon_name, color=ft.Colors.BLACK87, size=18),
                                bgcolor=ft.Colors.GREY_200,
                                padding=8,
                                border_radius=8
                            ),
                            # ft.Container(
                            #    content=ft.Text(tag_text, size=11, weight=ft.FontWeight.BOLD, color=tag_color),
                            #    bgcolor=tag_bg, padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                            #    border_radius=15
                            # )
                        ]
                    ),
                    ft.Container(height=10),
                    ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                    ft.Text(subtitle, size=12, color=ft.Colors.GREY_600),
                    ft.Container(height=15),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{current_val} / {target_val}", size=12, weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLACK87),
                            ft.Text(percentage_str, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)
                        ]
                    ),
                    ft.ProgressBar(value=progress_val, color=bar_color, bgcolor=ft.Colors.GREY_200, height=6),
                    ft.Container(height=10),
                    # ft.Container(
                    #    content=ft.Text("View Details", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                    #    alignment=ft.Alignment(0, 0),
                    #    bgcolor="#e9ebe8",
                    #    padding=10,
                    #    border_radius=6,
                    # )
                ]
            )
        )

    cards_row = ft.Row(
        spacing=20,
        scroll=ft.ScrollMode.AUTO,
        controls=[]
    )

    active_objectives = ft.Column(
        spacing=15,
        controls=[
            ft.Text(lang["saving.active_objectives"], size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
            cards_row
        ]
    )

    def create_transaction_row(icon_name, title, subtitle, amount, type_str, icon_color, icon_bg):
        return ft.Container(
            padding=ft.Padding.symmetric(vertical=15, horizontal=20),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=15,
                        controls=[
                            ft.Container(
                                content=ft.Icon(icon_name, size=20, color=icon_color),
                                bgcolor=icon_bg,
                                padding=12,
                                border_radius=10
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                                    ft.Text(subtitle, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600)
                                ]
                            )
                        ]
                    ),
                    ft.Column(
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Text(amount, size=15, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                            ft.Text(type_str, size=11, color=ft.Colors.GREY_400)
                        ]
                    )
                ]
            )
        )

    activity_section = ft.Container(
        bgcolor="#f3f5f1",
        border_radius=12,
        padding=ft.Padding.only(top=20, bottom=0),
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=20),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(lang["saving.recent_activity"], size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                            ft.Row([
                                ft.Text(lang["saving.export_ledger"], size=13, weight=ft.FontWeight.BOLD, color="#2e7d32"),
                                ft.Icon(ft.Icons.DOWNLOAD, size=14, color="#2e7d32")
                            ])
                        ]
                    )
                ),
                ft.Container(height=15),
                ft.Container(
                    padding=15,
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#e9ebe8",
                    border_radius=ft.BorderRadius.only(bottom_left=12, bottom_right=12),
                    content=ft.Text(lang["saving.view_transactions"], size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK_87)
                )
            ]
        )
    )

    center_container = ft.Container(
        content=ft.Column(
            spacing=35,
            controls=[
                top_nav_bar,
                header_section,
                dashboard_row,
                active_objectives,
                activity_section
            ]
        ),
        padding=25,
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
        route="/saving_goals",
        padding=0,
        bgcolor=ft.Colors.WHITE,
        controls=[
            ft.Stack(
                controls=[page_content, menu],
                expand=True
            )
        ]
    )