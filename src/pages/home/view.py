# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import CategorySelectionDialog, CompleteConfirmDialog, DeleteConfirmDialog, ExpenseInputDialog, FinancialChart, GoalDetailsDialog, IncomeInputDialog, ObjectiveSelectionDialog, QuickActionDialog, Menu, TopNavigationBar
from src.pages.home.components import ActionSelectionDialog, BalanceCard, SavingsProgressCard, ExpensePieChartCard, FeaturedLessonCard
from src.pages.home.logic import LogicController
from src.utils import Color, Text, UISettings

Logger.info("Initializing Home page...")


class HomeDialogManager:
    """Handles all dialog instantiation, states, and callbacks for the Home View."""
    def __init__(self, page: ft.Page, lang: dict, controller: LogicController, refresh_callback):
        self._page = page
        self.lang = lang
        self.controller = controller
        self.refresh_view = refresh_callback
        self.current_category_type = None

        # INITIALIZE DIALOG COMPONENTS
        self.quick_action_dialog = QuickActionDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.complete_confirm_dialog = CompleteConfirmDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.delete_confirm_dialog = DeleteConfirmDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.goal_details_dialog = GoalDetailsDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_complete=lambda ftpage, objective_id: self.complete_confirm_dialog.trigger(ftpage, objective_id),
            on_quick_action=lambda ftpage, objective_id, action: self.quick_action_dialog.trigger(ftpage, objective_id, action),
            on_delete=lambda ftpage, objective_id: self.delete_confirm_dialog.trigger(ftpage, objective_id)
        )

        self.saving_dialog = ObjectiveSelectionDialog(
            page=self._page,
            lang=self.lang,
            controller=self.controller,
            on_select=self.handle_objective_selected
        )

        self.action_dialog = ActionSelectionDialog(
            page=self._page,
            lang=self.lang,
            on_income=self.open_income_dialog,
            on_expense=self.open_expense_dialog,
            on_saving=self.open_saving_dialog,
            on_cancel=self.close_all
        )

        self.category_dialog = CategorySelectionDialog(
            page=self._page,
            lang=self.lang,
            on_select=self.handle_category_selected
        )

        self.income_dialog = IncomeInputDialog(
            page=self._page,
            lang=self.lang,
            on_save=self.handle_save_income,
            on_cancel=self.close_all,
            on_category_click=lambda e: self.open_category_selector("income")
        )

        self.expense_dialog = ExpenseInputDialog(
            page=self._page,
            lang=self.lang,
            on_save=self.handle_save_expense,
            on_cancel=self.close_all,
            on_category_click=lambda e: self.open_category_selector("expense")
        )

    def close_all(self, e=None):
        dialogs = [
            self.action_dialog,
            self.income_dialog,
            self.expense_dialog,
            self.category_dialog,
            self.saving_dialog,
            self.goal_details_dialog,
            self.quick_action_dialog,
            self.complete_confirm_dialog,
            self.delete_confirm_dialog
        ]
        for dialog in dialogs:
            if dialog:
                dialog.open = False
        self._page.update()
        return e

    def _open_dialog(self, dialog):
        self.close_all()
        if dialog not in self._page.overlay:
            self._page.overlay.append(dialog)
        dialog.open = True
        self._page.update()

    def open_action_dialog(self, e=None):
        if self.action_dialog not in self._page.overlay:
            self._page.overlay.append(self.action_dialog)
        self.action_dialog.open = True
        self._page.update()
        return e

    def open_income_dialog(self, e=None):
        self._open_dialog(self.income_dialog)
        return e

    def open_expense_dialog(self, e=None):
        self._open_dialog(self.expense_dialog)
        return e

    def open_saving_dialog(self, e=None):
        self.close_all()
        if self.saving_dialog not in self._page.overlay:
            self._page.overlay.append(self.saving_dialog)
        self.saving_dialog.load_objectives(self._page)
        self.saving_dialog.open = True
        self._page.update()
        return e

    def open_category_selector(self, category_type: str):
        self.current_category_type = category_type
        if self.category_dialog not in self._page.overlay:
            self._page.overlay.append(self.category_dialog)
        self.category_dialog.load_categories(category_type)
        self.category_dialog.open = True
        self._page.update()

    def handle_category_selected(self, category_name: str):
        if self.current_category_type == "expense":
            self.expense_dialog.set_category(category_name)
        elif self.current_category_type == "income":
            self.income_dialog.set_category(category_name)
        self.category_dialog.open = False
        self._page.update()

    def handle_objective_selected(self, ftpage, objective_id, title, reason, cur, tgt, prog, comp):
        self.goal_details_dialog.trigger(ftpage, objective_id, title, reason, cur, tgt, prog, comp)
        self.saving_dialog.open = False
        self._page.update()

    def handle_save_income(self, e=None):
        vals = self.income_dialog.get_values()
        success, message = self.controller.add_income_entry(vals)

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

        if success:
            self.income_dialog.clear()
            self.close_all()
            self.refresh_view()
        else:
            self._page.update()

        return e

    def handle_save_expense(self, e=None):
        vals = self.expense_dialog.get_values()
        success, message = self.controller.add_expense_entry(vals)

        self._page.snack_bar = ft.SnackBar(Text.MEDIUM(message))
        self._page.snack_bar.open = True

        if success:
            self.expense_dialog.clear()
            self.close_all()
            self.refresh_view()
        else:
            self._page.update()

        return e


class HomeView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_info: dict):
        self._page = page
        self.lang = lang
        self.user_info = user_info

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_info["username"])

        # INITIALIZE DIALOG MANAGER
        self.dialogs = HomeDialogManager(self._page, self.lang, self.controller, self.refresh_view)

        # FETCH DASHBOARD DATA
        self.metrics, self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()
        self.ai_advice = self.controller.get_ai_advice(
            self.metrics["net_balance"],
            self.metrics["total_income"],
            self.metrics["total_expense"]
        )
        self.objectives = self.controller.get_user_objectives() or []

        # INITIALIZE PAGE COMPONENTS
        self.menu = Menu(self._page, self.lang, self.user_info)
        self.top_navigation_bar = TopNavigationBar(page=self._page, lang=self.lang, current_user=self.user_info["username"])

        self.balance_card = BalanceCard(
            page=self._page,
            lang=self.lang,
            net_balance=self.metrics["net_balance"],
            income=self.metrics["total_income"],
            expense=self.metrics["total_expense"],
            saving=self.metrics["total_savings"],
            ai_advice=self.ai_advice,
            on_add_click=self.dialogs.open_action_dialog,
            on_scan_click=lambda e: self._page.go("/purchase_scanner")
        )

        self.financial_chart = FinancialChart(page=self._page, lang=self.lang, chart_date=self.chart_date, chart_data=self.chart_data, chart_type=self.chart_type)
        self.savings_progress_card = SavingsProgressCard(
            page=self._page,
            lang=self.lang,
            objective_items=self.controller.get_saving_progress_items(self.objectives, self.lang)
        )
        self.expense_pie_chart = ExpensePieChartCard(
            page=self._page,
            lang=self.lang,
            category_data=self.metrics["category_expenses"]
        )
        self.featured_lesson_card = FeaturedLessonCard(self._page, self.lang)

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            content=ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Container(
                        width=UISettings.MAX_APP_WIDTH,
                        padding=UISettings.CARD_PADDING,
                        content=ft.Column(
                            spacing=20,
                            expand=True,
                            controls=[
                                self.balance_card,
                                self.financial_chart,
                                self.expense_pie_chart,
                                self.savings_progress_card,
                                self.featured_lesson_card
                            ]
                        )
                    )
                ]
            ),
            expand=True,
            padding=0,
            margin=ft.Margin(top=UISettings.TOP_NAVIGATION_HEIGHT, bottom=UISettings.MENU_HEIGHT)
        )

        super().__init__(
            route="/home",
            padding=0,
            bgcolor=Color.PAGE_BACKGROUND,
            horizontal_alignment=ft.MainAxisAlignment.CENTER,
            controls=ft.Stack(
                expand=True,
                controls=[
                    self.main_container,
                    self.top_navigation_bar,
                    self.menu
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def refresh_view(self) -> None:
        for control in self._page.overlay:
            control.open = False

        self._page.update()

    def get_safe_page_size(self) -> tuple[int, int]: # -> (width, height)
        # Get page width and height if available, return fallback values otherwise
        current_width: float = self._page.width or UISettings.MAX_APP_WIDTH
        current_height: float = self._page.height or UISettings.MAX_APP_HEIGHT

        # Make sure width and height don't exceed max values
        safe_width = min(int(current_width), UISettings.MAX_APP_WIDTH)
        safe_height = min(int(current_height), UISettings.MAX_APP_HEIGHT)

        return safe_width, safe_height

    def on_page_resize(self, e=None) -> None:
        page_width, page_height = self.get_safe_page_size()

        self.main_container.width = page_width

        self.dialogs.action_dialog.resize(
            dialog_width=int(page_width * 0.5),
            button_width=int(page_width * 0.4),
            button_height=int(page_height * 0.1)
        )

        self.dialogs.category_dialog.resize(
            dialog_width=int(page_width * 0.9),
        )

        self.menu.resize(page_width)
        self.top_navigation_bar.resize(page_width)

        return e

def get_home_view(page: ft.Page, lang: dict, user_info: dict) -> ft.View:
    return HomeView(page, lang, user_info)
