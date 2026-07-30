# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import flet as ft

from src.logger import Logger
from src.pages.global_components import QuickActionDialog, CompleteConfirmDialog, DeleteConfirmDialog, SideMenu, TopNavigationBar, FinancialChart, CategorySelectionDialog, IncomeInputDialog, ExpenseInputDialog, GoalDetailsDialog, ObjectiveSelectionDialog
from src.pages.home.components import ActionSelectionDialog, BalanceCard, SavingGauge
from src.pages.home.logic import LogicController
from src.utils import apply_responsive_text, Color, Text, UISettings


Logger.info("Initializing Home page...")


class HomeView(ft.View):
    def __init__(self, page: ft.Page, lang: dict, user_state: dict):
        self._page = page
        self.lang = lang
        self.user_state = user_state

        # INITIALIZE PAGE CONTROLLER
        self.controller = LogicController(self.user_state["username"])

        # INITIALIZE PAGE COMPONENTS
        self.current_category_type = None
        self.menu = SideMenu(self._page, self.lang, self.user_state)
        self.top_navigation_bar = TopNavigationBar(menu_button=self.menu.menu_button, current_user=self.user_state["current_user"])

        self.quick_action_dialog = QuickActionDialog(
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.complete_confirm_dialog = CompleteConfirmDialog(
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.delete_confirm_dialog = DeleteConfirmDialog(
            lang=self.lang,
            controller=self.controller,
            on_success=self.refresh_view
        )

        self.goal_details_dialog = GoalDetailsDialog(
            lang=self.lang,
            controller=self.controller,
            on_complete=lambda ftpage, objective_id: self.complete_confirm_dialog.trigger(ftpage, objective_id),
            on_quick_action=lambda ftpage, objective_id, action: self.quick_action_dialog.trigger(ftpage, objective_id, action),
            on_delete=lambda ftpage, objective_id: self.delete_confirm_dialog.trigger(ftpage, objective_id)
        )

        self.saving_dialog = ObjectiveSelectionDialog(self.lang, self.controller, self.handle_objective_selected)

        self.action_dialog = ActionSelectionDialog(
            lang=self.lang,
            on_income=self.open_income_dialog,
            on_expense=self.open_expense_dialog,
            on_saving=self.open_saving_dialog,
            on_cancel=self.close_all_dialogs
        )
        self.category_dialog = CategorySelectionDialog(on_select=self.handle_category_selected)
        self.income_dialog = IncomeInputDialog(
            on_save=self.handle_save_income,
            on_cancel=self.close_all_dialogs,
            on_category_click=lambda e: self.open_category_selector("income")
        )
        self.expense_dialog = ExpenseInputDialog(
            on_save=self.handle_save_expense,
            on_cancel=self.close_all_dialogs,
            on_category_click=lambda e: self.open_category_selector("expense")
        )

        self.balance_card = BalanceCard(
            lang=self.lang,
            expense=0,
            income=0,
            saving=0,
            on_add_click=self.open_action_dialog
        )

        self.total_savings, self.total_target, self.chart_date, self.chart_data, self.chart_type = self.controller.get_dashboard_data()

        self.financial_chart = FinancialChart(self.chart_date, self.chart_data, self.chart_type, self.lang)
        self.saving_gauge = SavingGauge(self._page, self.total_savings, self.total_target, self.lang)

        # Move this to components when the feature is actually implemented
        self.recent_lesson = ft.Container(
            content=ft.Container(
                content=Text.H4("Bài 1: Bản chất của tiền", color=Color.DEFAULT_TEXT, align=ft.Alignment.CENTER),
                border=ft.Border.all(1, ft.Colors.GREY_400),
                padding=5,
                border_radius=12,
                aspect_ratio=3,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=Color.WHITE,
            padding=UISettings.CARD_PADDING,
            expand=1,
            aspect_ratio=1.0,
            shadow=ft.BoxShadow(spread_radius=UISettings.SHADOW_SPREAD, blur_radius=UISettings.SHADOW_BLUR, color=Color.SHADOW),
        )

        # INITIALIZE MAIN CONTAINER
        self.main_container = ft.Container(
            width=UISettings.MAX_APP_WIDTH,
            padding=UISettings.CARD_PADDING,
            content=ft.Column(
                spacing=20,
                controls=[
                    self.top_navigation_bar,
                    self.balance_card,
                    self.financial_chart,
                    ft.Row([self.saving_gauge, self.recent_lesson])
                ]
            )
        )

        super().__init__(
            route="/home",
            padding=0,
            bgcolor=Color.WHITE,
            controls=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[self.main_container]
                                )
                            ]
                        ),
                        expand=True,
                        padding=0
                    ),
                    self.menu.view
                ]
            )
        )

        self._page.on_resize = self.on_page_resize
        self.on_page_resize()

    def refresh_view(self):
        for control in self._page.overlay:
            control.open = False

        if len(self._page.views) > 0:
            self._page.views[-1].controls.clear()
            self._page.views[-1].controls.extend(get_home_view(self._page, self.lang, self.user_state).controls)

        self._page.update()

    def open_action_dialog(self, e):
        if self.action_dialog not in self._page.overlay:
            self._page.overlay.append(self.action_dialog)
        self.action_dialog.open = True
        self._page.update()
        return e

    def close_all_dialogs(self, e=None):
        if hasattr(self, 'action_dialog'): self.action_dialog.open = False
        if hasattr(self, 'income_dialog'): self.income_dialog.open = False
        if hasattr(self, 'expense_dialog'): self.expense_dialog.open = False
        if hasattr(self, 'category_dialog'): self.category_dialog.open = False
        if hasattr(self, 'saving_dialog') and self.saving_dialog: self.saving_dialog.open = False
        if hasattr(self, 'goal_details_dialog') and self.goal_details_dialog: self.goal_details_dialog.open = False
        if hasattr(self, 'quick_action_dialog') and self.quick_action_dialog: self.quick_action_dialog.open = False
        if hasattr(self, 'complete_confirm_dialog') and self.complete_confirm_dialog: self.complete_confirm_dialog.open = False
        if hasattr(self, 'delete_confirm_dialog') and self.delete_confirm_dialog: self.delete_confirm_dialog.open = False
        self._page.update()
        return e

    def open_income_dialog(self, e):
        self.close_all_dialogs()
        if self.income_dialog not in self._page.overlay:
            self._page.overlay.append(self.income_dialog)
        self.income_dialog.open = True
        self._page.update()
        return e

    def open_expense_dialog(self, e):
        self.close_all_dialogs()
        if self.expense_dialog not in self._page.overlay:
            self._page.overlay.append(self.expense_dialog)
        self.expense_dialog.open = True
        self._page.update()
        return e

    def open_saving_dialog(self, e):
        self.close_all_dialogs()
        if self.saving_dialog not in self._page.overlay:
            self._page.overlay.append(self.saving_dialog)
        self.saving_dialog.load_objectives(self._page)
        self.saving_dialog.open = True
        self._page.update()
        return e

    def handle_objective_selected(self, ftpage, objective_id, title, reason, cur, tgt, prog, comp):
        self.goal_details_dialog.trigger(ftpage, objective_id, title, reason, cur, tgt, prog, comp)
        self.saving_dialog.open = False
        self._page.update()

    def open_category_selector(self, category_type: str):
        self.current_category_type = category_type
        if self.category_dialog not in self._page.overlay:
            self._page.overlay.append(self.category_dialog)
            self._page.update()
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

    def handle_save_income(self, e):
        vals = self.income_dialog.get_values()
        amount = vals["amount"]
        category = vals["category"]
        note = vals["note"]
        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return e
        try:
            if self.controller.add_income_entry(amount, category, note):
                self.income_dialog.clear()
                self.close_all_dialogs()
                self._page.snack_bar = ft.SnackBar(Text.LABEL("Income added successfully!"))
                self._page.snack_bar.open = True
                self.refresh_view()
        except ValueError:
            Logger.error("Invalid amount provided")

        return e

    def handle_save_expense(self, e):
        vals = self.expense_dialog.get_values()
        amount = vals["amount"]
        category = vals["category"]
        note = vals["note"]
        if not amount or not category:
            Logger.warning("Amount or Category missing.")
            return e
        try:
            if self.controller.add_expense_entry(amount, category, note):
                self.expense_dialog.clear()
                self.close_all_dialogs()
                self._page.snack_bar = ft.SnackBar(Text.LABEL("Expense added successfully!"))
                self._page.snack_bar.open = True
                self.refresh_view()
        except ValueError:
            Logger.error("Invalid amount provided")

        return e

    def on_page_resize(self, e=None):
        current_width = self._page.width if e is None else e.width
        if not current_width: current_width = UISettings.MAX_APP_WIDTH
        safe_width = int(min(current_width, UISettings.MAX_APP_WIDTH))

        self.balance_card.width = safe_width
        self.top_navigation_bar.width = safe_width * 0.9
        self.main_container.width = safe_width
        self.saving_gauge.resize(safe_width)

        apply_responsive_text(self.main_container, safe_width)

        try:
            self.update()
        except RuntimeError as e:
            Logger.debug(f"Skipped updating during resize: {e}")

def get_home_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    return HomeView(page, lang, user_state)
