import flet as ft
import csv
from datetime import date
from src.pages.global_elements.menu import SideMenu
import src.database as db


def get_savings_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    menu = SideMenu(page, lang, user_state)
    menu_button = menu.menu_button
    current_user = user_state.get("current_user", "Admin")

    total_savings = db.get_total_savings(current_user)
    total_target = db.get_total_target_amount(current_user)

    if total_target > 0:
        total_progress_val = min(total_savings / total_target, 1.0)
        total_percentage_str = f"{(float(total_progress_val) * 100):.2f}%"
    else:
        total_progress_val = 0.0
        total_percentage_str = "0%"

    top_nav_bar = ft.Row([ft.Container(content=menu_button, alignment=ft.Alignment.CENTER)],
                         alignment=ft.MainAxisAlignment.START)

    goal_title_input = ft.TextField(label=lang["saving.goal_title"])
    goal_amount_input = ft.TextField(label=lang["saving.target_amount"], input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""))
    reason_input = ft.TextField(label=lang["saving.reason"])

    def close_obj_dlg(e):
        new_objective_dlg.open = False
        page.update()

    def create_objective_card(obj_title, subtitle, current_val, target_val, percentage, progress):
        return ft.Container(
            width=260, bgcolor=ft.Colors.WHITE, border_radius=12, padding=20,
            border=ft.border.all(1, ft.Colors.GREY_200),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Text(obj_title, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                    ft.Text(subtitle, size=12, color=ft.Colors.GREY_600),
                    ft.Container(height=15),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"{current_val} / {target_val}", size=12, weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLACK87),
                            ft.Text(percentage, size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87)
                        ]
                    ),
                    ft.ProgressBar(value=progress, color="#2e7d32", bgcolor="#dcedc8", height=6),
                    ft.Container(height=10),
                ]
            )
        )

    existing_objectives = db.get_user_objectives(current_user)
    initial_cards = []

    for obj in existing_objectives:
        obj_id, title, reason, target_amount = obj
        obj_savings = db.get_objective_progress(obj_id)

        if target_amount > 0:
            raw_progress = obj_savings / target_amount
            progress_val = min(raw_progress, 1.0)
            percentage_str = f"{int(progress_val * 100)}%"
        else:
            progress_val = 0.0
            percentage_str = "0%"

        title_display = f"✅ {title}" if progress_val >= 1.0 else title

        card = create_objective_card(
            obj_title=title_display,
            subtitle=reason,
            current_val=f"{int(obj_savings):,} VND",
            target_val=f"{int(target_amount):,} VND",
            percentage=percentage_str,
            progress=progress_val,
        )
        initial_cards.append(card)

    cards_row = ft.Row(spacing=20, scroll=ft.ScrollMode.AUTO, controls=initial_cards)

    def add_objective(e):
        obj_title = goal_title_input.value if goal_title_input.value else lang["saving.untitled_goal"]
        subtitle = reason_input.value if reason_input.value else lang["saving.no_reason"]

        try:
            target = int(goal_amount_input.value)
        except:
            target = 0

        if db.add_objective(current_user, obj_title, subtitle, target):
            new_objective_dlg.open = False
            page.go("/saving")
            page.update()

    new_objective_dlg = ft.AlertDialog(
        title=ft.Text(lang["saving.create_objectives"]),
        content=ft.Column(tight=True, controls=[goal_title_input, goal_amount_input, reason_input]),
        actions=[
            ft.TextButton(lang["generic.cancel"], on_click=close_obj_dlg),
            ft.Button(lang["saving.save_objective"], on_click=add_objective, bgcolor="#1d7333", color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_new_objective(e):
        if new_objective_dlg not in page.overlay: page.overlay.append(new_objective_dlg)
        new_objective_dlg.open = True
        page.update()

    add_amount_input = ft.TextField(label="Amount (VND)", input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""), width=300)

    dropdown_options = [ft.dropdown.Option(key="0", text="General Savings (No Objective)")]
    for obj in existing_objectives:
        dropdown_options.append(ft.dropdown.Option(key=str(obj[0]), text=obj[1]))

    objective_dropdown = ft.Dropdown(label="Allocate to Objective", options=dropdown_options, value="0", width=300)

    selected_date = date.today()
    date_text = ft.Text(selected_date.strftime("%B %d, %Y"), size=16, color=ft.Colors.BLACK87)

    def on_date_change(e):
        nonlocal selected_date
        selected_date = e.control.value
        date_text.value = selected_date.strftime("%B %d, %Y")
        page.update()

    date_picker = ft.DatePicker(on_change=on_date_change, first_date=date(2000, 1, 1), last_date=date.today())

    def open_date_picker(e):
        if date_picker not in page.overlay: page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    def add_contribution(e):
        try:
            amount = float(add_amount_input.value)
            if amount <= 0: raise ValueError

            date_str = selected_date.strftime("%Y-%m-%d")
            selected_obj_id = int(objective_dropdown.value)

            if db.add_saving_entry(current_user, amount, date_str, selected_obj_id):
                add_saving_dlg.open = False
                page.go("/saving")
                page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text(f"Error: User '{current_user}' not found."))
                page.snack_bar.open = True
                page.update()

        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a valid amount."))
            page.snack_bar.open = True
            page.update()

    add_saving_dlg = ft.AlertDialog(
        title=ft.Text("Add Daily Savings", weight=ft.FontWeight.BOLD),
        content=ft.Column(
            tight=True,
            controls=[
                objective_dropdown,
                add_amount_input,
                ft.Container(height=10),
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.GREY_400),
                    date_text,
                    ft.TextButton("Change Date", on_click=open_date_picker)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]
        ),
        actions=[
            ft.TextButton("Cancel", on_click=lambda e: setattr(add_saving_dlg, 'open', False) or page.update()),
            ft.ElevatedButton("Add Contribution", on_click=add_contribution, bgcolor="#004D40", color=ft.Colors.WHITE),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def open_add_saving(e):
        if add_saving_dlg not in page.overlay: page.overlay.append(add_saving_dlg)
        add_saving_dlg.open = True
        page.update()


    async def trigger_export(e):
        file_path = await ft.FilePicker().save_file(
            allowed_extensions=["csv"],
            file_name="savings_ledger.csv"
        )

        if file_path:
            activities = db.get_user_activity(current_user)
            try:
                with open(file_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Date", "Action Type", "Description"])
                    for act in activities:
                        writer.writerow([act["date"], act["type"], act["desc"]])
                page.snack_bar = ft.SnackBar(ft.Text("Ledger successfully exported!"))
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {str(ex)}"))

            page.snack_bar.open = True
            page.update()

    activity_data = db.get_user_activity(current_user)
    activity_controls = []

    if not activity_data:
        activity_controls.append(ft.Text("No recent activity.", color=ft.Colors.GREY_500, italic=True))
    else:
        for item in activity_data:
            icon_used = ft.Icons.ATTACH_MONEY if item["type"] == "saving" else ft.Icons.FLAG
            icon_color = "#1d7333" if item["type"] == "saving" else "#d32f2f"

            activity_controls.append(
                ft.ListTile(
                    leading=ft.Icon(icon_used, color=icon_color),
                    title=ft.Text(item["desc"], size=14, weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(item["date"], size=12, color=ft.Colors.GREY_600)
                )
            )

    header_section = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                spacing=5,
                controls=[
                    ft.Text(lang["saving.title"], size=32, weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK87),
                    ft.Text(lang["saving.description"], size=14, color=ft.Colors.GREY_800)
                ]
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Button("Add Saving", color=ft.Colors.WHITE, bgcolor="#004D40", height=45, icon=ft.Icons.ADD,
                              on_click=open_add_saving),
                    ft.Button(lang["saving.create_objectives"], color=ft.Colors.WHITE,
                              bgcolor="#1d7333", height=45, on_click=open_new_objective)
                ]
            )
        ]
    )

    aggregate_card = ft.Container(
        expand=2, bgcolor="#f0f5ee", height=200, border_radius=12, padding=25,
        content=ft.Column(
            spacing=8, alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Text(lang["saving.aggregate_portfolio_value"], size=11,
                        weight=ft.FontWeight.BOLD, color="#5a7a5d"),
                ft.Text(f"{int(total_savings):,} VND", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Container(height=15),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text(lang["saving.progression"], size=13, color=ft.Colors.BLACK_87),
                        ft.Text(total_percentage_str, size=13, weight=ft.FontWeight.BOLD, color="#1d7333")
                    ]
                ),
                ft.ProgressBar(value=total_progress_val, color="#2e7d32", bgcolor="#dcedc8", height=8)
            ]
        )
    )

    on_track_card = ft.Container(expand=1, bgcolor="#145c26", height=200, border_radius=12, padding=25,
                                 content=ft.Column(spacing=10))
    dashboard_row = ft.Row(spacing=20, controls=[aggregate_card, on_track_card])

    active_objectives = ft.Column(
        spacing=15, controls=[
            ft.Text(lang["saving.active_objectives"], size=22, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLACK87), cards_row]
    )

    activity_section = ft.Container(
        bgcolor="#f3f5f1", border_radius=12, padding=ft.Padding.only(top=20, bottom=0),
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=20),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(lang["saving.recent_activity"], size=18,
                                    weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK87),
                            ft.GestureDetector(
                                on_tap=trigger_export,
                                content=ft.Row([
                                    ft.Text(lang["saving.export_ledger"], size=13,
                                            weight=ft.FontWeight.BOLD, color="#2e7d32"),
                                    ft.Icon(ft.Icons.DOWNLOAD, size=14, color="#2e7d32")
                                ])
                            )
                        ]
                    )
                ),
                ft.Container(height=15),
                ft.Container(
                    padding=10,
                    content=ft.Column(controls=activity_controls, height=200, scroll=ft.ScrollMode.AUTO)
                )
            ]
        )
    )

    center_container = ft.Container(
        content=ft.Column(spacing=35,
                          controls=[top_nav_bar, header_section, dashboard_row, active_objectives, activity_section]),
        padding=25, width=650
    )

    page_content = ft.Container(content=ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, controls=[
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[center_container])]), expand=True, padding=0)

    def on_page_resize(e) -> None:
        safe_width = min((page.width if e is None else e.width) or 650, 650)
        try:
            center_container.width = safe_width
            page.update()
        except Exception:
            pass

    page.on_resize = on_page_resize
    on_page_resize(None)

    return ft.View(
        route="/saving",
        padding=0,
        bgcolor=ft.Colors.WHITE,
        controls=[
            ft.Stack(
                controls=[page_content, menu],
                expand=True
            )
        ]
    )