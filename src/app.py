import src.database as db
import flet as ft

from src.pages.add_saving import get_add_saving_view
from src.utils import get_language
from src.pages.home import get_home_view
from src.pages.login import get_login_view
from src.pages.lessons import get_lessons_view
from src.pages.saving import get_savings_view

async def main(page: ft.Page) -> None:
    db.init()

    lang = get_language("vi")
    user_state = {
        "current_user": None
    }

    page.title = "Finam"
    page.padding = 0
    page.window.resizable = False # SWITCH TO FALSE WHEN DONE WITH TESTING
    page.window.width = 650
    page.window.height = 1000
    page.bgcolor = ft.Colors.WHITE
    page.update()

    def route_change(route) -> None:
        page.views.clear()

        if page.route == "/login":
            page.views.append(get_login_view(page, lang, user_state))
        elif page.route == "/home":
            page.views.append(get_home_view(page, lang, user_state))
        elif page.route == "/lessons":
            page.views.append(get_lessons_view(page, lang, user_state))
        elif page.route == "/saving":
            page.views.append(get_savings_view(page, lang, user_state))
        elif page.route == "/add_saving":
            page.views.append(get_add_saving_view(page, lang, user_state))


        page.update()

    async def view_pop(view) -> None:
        page.views.pop()
        top_view = page.views[-1]
        await page.push_route(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await page.push_route("/login")