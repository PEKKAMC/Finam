import flet as ft
import src.database as db

def get_login_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    txt_new_user = ft.TextField(label=lang["login.add_user"], expand=True, color=ft.Colors.GREY_900, on_submit=lambda e: add_user(e))
    txt_error = ft.Text("", color=ft.Colors.RED)
    users_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
    users = db.get_all_users()

    def refresh_user_list() -> None:
        users_column.controls.clear()
        current_users = db.get_all_users()

        if not current_users:
            users_column.controls.append(
                ft.Text(lang["login.no_user"], color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
            )

        for u in current_users:
            def get_select_handler(name):
                async def handler(e) -> None:
                    user_state["current_user"] = name
                    await page.push_route("/home")
                return handler

            def get_delete_handler(name):
                def handler(e) -> None:
                    def confirm_delete(e_dialog) -> None:
                        db.delete_user(name)
                        refresh_user_list()

                        if name in users:
                            users.remove(name)
                            refresh_user_list()

                        delete_dialog.open = False
                        page.update()

                    def cancel_delete(e_dialog) -> None:
                        delete_dialog.open = False
                        page.update()

                    delete_dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text(lang["login.confirm_delete_user_title"]),
                        content=ft.Text(lang["login.confirm_delete_user_content"]),
                        actions=[
                            ft.TextButton(lang["generic.cancel"], on_click=cancel_delete),
                            ft.TextButton(lang["generic.delete"], on_click=confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )
                    page.overlay.append(delete_dialog)
                    delete_dialog.open = True
                    page.update()
                return handler

            user_row = ft.Row([
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_GREY_900),
                        ft.Text(u, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                    ]),
                    bgcolor=ft.Colors.GREY_100,
                    padding=10,
                    border_radius=10,
                    ink=True,
                    expand=True,
                    on_click=get_select_handler(u)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    icon_color=ft.Colors.RED_400,
                    tooltip=lang["login.delete_user_tooltip"],
                    on_click=get_delete_handler(u)
                )
            ])
            users_column.controls.append(user_row)
        page.update()

    def add_user(e) -> None:
        input_user = txt_new_user.value.strip()
        if input_user and input_user not in users:
            db.add_user(input_user)
            users.append(input_user)
            txt_new_user.value = ""
            txt_error.value = ""
            refresh_user_list()
        elif input_user in users:
            txt_error.value = lang["login.user_already_exists"]
        else:
            txt_error.value = lang["login.invalid_username"]
        page.update()

    btn_add_user = ft.IconButton(
        icon=ft.Icons.ADD,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.BLUE_GREY_900,
        icon_size=24,
        on_click=add_user
    )

    refresh_user_list()

    return ft.View(
        route="/login",
        bgcolor=ft.Colors.WHITE,
        controls=[
            ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.PEOPLE_ALT, size=80, color=ft.Colors.BLUE_GREY_900),
                        ft.Text(lang["login.select_user"], size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900),
                        ft.Row([txt_new_user, btn_add_user], alignment=ft.MainAxisAlignment.CENTER),
                        txt_error,
                        ft.Container(
                            content=users_column,
                            height=350,
                            border=ft.Border.all(1, ft.Colors.GREY_300),
                            border_radius=10,
                            padding=10
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20
                ),
                alignment=ft.Alignment.CENTER,
                width=500,
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        vertical_alignment=ft.MainAxisAlignment.CENTER
    )