import flet as ft
from datetime import date
import src.database as db
from src.pages.global_elements.menu import SideMenu


# Use the same language dictionary structure as in home.py
def get_add_saving_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    menu = SideMenu(page, lang, user_state)
    menu_button = menu.menu_button

    current_amount = ft.TextField(value="0.00", text_size=40, text_align=ft.TextAlign.RIGHT,
                                  border=ft.InputBorder.NONE, keyboard_type=ft.KeyboardType.NUMBER, width=200)
    note_input = ft.TextField(label="Coffee money, Loose change...", multiline=True, min_lines=3, border_color=ft.Colors.GREY_300)
    selected_date = date.today()
    date_text = ft.Text(selected_date.strftime("%B %d, %Y"), size=16, color=ft.Colors.BLACK)

    header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Container(content=menu_button, alignment=ft.Alignment.CENTER),
            ft.Text("Add Daily Savings", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
            ft.Container(
                content=ft.Image(src="/character.png", width=40, height=40, border_radius=20),  # Use your avatar image
                on_click=lambda _: page.go("/settings")  # Assuming settings is the avatar destination
            )
        ]
    )

    # --- Today's Contribution Input ---
    contribution_display = ft.Container(
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("TODAY'S CONTRIBUTION", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text("$", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_300),
                        current_amount,
                    ]
                ),
                ft.Text("Grow your wealth, one dollar at a time.", size=14, color=ft.Colors.GREY_700),
            ]
        ),
        padding=ft.Padding(0, 40, 0, 40)
    )

    # --- Date Selection Card ---
    def on_date_change(e):
        s_date = e.control.value
        date_text.value = s_date.strftime("%B %d, %Y")
        page.update()

    date_picker = ft.DatePicker(
        on_change=on_date_change,
        first_date=date(2022, 1, 1),
        last_date=date(2030, 12, 31),
    )
    page.overlay.append(date_picker)

    date_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("SELECT DATE", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_MONTH, color=ft.Colors.GREY_400),
                            ft.Column([
                                ft.Text("Today", size=16, weight=ft.FontWeight.BOLD),
                                date_text,
                            ], spacing=0)
                        ]),
                        ft.TextButton("Change", on_click=lambda _: date_picker.date_picker_mode)
                    ]
                )
            ]
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20,
        margin=ft.Margin(0, 10, 0, 10)
    )

    # --- Optional Note Card ---
    tags = ["Lunch", "Commute", "Round-up"]
    tag_chips = ft.Row(
        controls=[
            ft.Chip(
                label=ft.Text(tag),
                on_select=lambda e, t=tag: (
                    setattr(note_input, "value", f"{note_input.value} {t}".strip()),
                    note_input.update()
                )
            ) for tag in tags
        ],
        spacing=10
    )

    note_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("OPTIONAL NOTE", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                note_input,
                tag_chips,
            ]
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20,
        margin=ft.Margin(0, 10, 0, 10)
    )

    # --- Projected Growth Card ---
    projected_text = ft.Text("Saving $0 daily could grow to $0 in one year.", size=14, color=ft.Colors.WHITE)

    def update_projection(e):
        try:
            daily_saving = float(current_amount.value)
            yearly_growth = daily_saving * 365
            # Basic calculation, not including interest for simplicity
            projected_text.value = f"Saving ${daily_saving:,.2f} daily could grow to ${yearly_growth:,.0f} in one year."
        except ValueError:
            projected_text.value = "Saving $0 daily could grow to $0 in one year."
        page.update()

    current_amount.on_change = update_projection

    growth_card = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.SHOW_CHART, color=ft.Colors.GREEN_400),
                    ft.Text("Projected Growth", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ]),
                projected_text,
                ft.ProgressBar(value=0.5, color=ft.Colors.GREEN_ACCENT, bgcolor="#004D40", height=10,
                               border_radius=5)
            ]
        ),
        bgcolor="#004D40",
        border_radius=15,
        padding=20,
        margin=ft.Margin(0, 20, 0, 20)
    )

    # --- Add Contribution Button ---
    def add_contribution(e):
        try:
            amount = float(current_amount.value)
            if amount <= 0:
                raise ValueError

            username = user_state.get("current_user")
            date_str = selected_date.strftime("%Y-%m-%d")
            note = note_input.value

            # Save to database
            if db.add_saving_entry(username, amount, date_str, note):
                # Success
                page.snack_bar = ft.SnackBar(ft.Text(f"Added ${amount:,.2f} to savings!"))
                page.snack_bar.open = True
                current_amount.value = "0.00"
                note_input.value = ""
                page.update()
                # Optional: Navigate back to savings overview
                # page.go("/saving")
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Error adding savings. User not found."))
                page.snack_bar.open = True
                page.update()

        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a valid amount."))
            page.snack_bar.open = True
            page.update()

    add_button = ft.ElevatedButton(
        "Add Contribution",
        icon=ft.Icons.ADD,
        bgcolor="#004D40",
        color=ft.Colors.WHITE,
        height=50,
        on_click=add_contribution,
        width=float('inf')  # Full width
    )

    # --- Main Content Structure ---
    center_container = ft.Container(
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                header,
                contribution_display,
                date_card,
                note_card,
                growth_card,
                add_button,
                ft.Container(height=100)  # Spacing for bottom nav
            ]
        ),
        padding=20,
        width=650,
        bgcolor="#F5F5F7",
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

    return ft.View(
        route="/add_saving",
        padding=0,
        bgcolor="#F5F5F7",
        controls=[
            ft.Stack(
                controls=[
                    page_content,
                ],
                expand=True
            )
        ]
    )