import flet as ft
import flet_charts as fc
import random

from src.pages.global_elements.menu import SideMenu

def get_home_view(page: ft.Page, lang: dict, user_state: dict) -> ft.View:
    menu = SideMenu(page, lang, user_state)
    menu_button = menu.menu_button

    username = ft.Text(
        value=user_state.get("current_user", "Unknown"),
        size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.BLACK
    )

    char_image = ft.Image(src="/character.png", border_radius=10)

    def create_object(text, shape=ft.BoxShape.RECTANGLE, expand=1, is_square=False, aspect_ratio=None) -> ft.Container:
        inner_card = ft.Container(
            content=ft.Text(text, size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, color=ft.Colors.WHITE),
            bgcolor=ft.Colors.WHITE,
            shape=shape,
            border_radius=10 if shape == ft.BoxShape.RECTANGLE else None,
            alignment=ft.Alignment.CENTER,
            padding=10,
        )
        if is_square:
            inner_card.aspect_ratio = 1.0
        elif aspect_ratio:
            inner_card.aspect_ratio = aspect_ratio
        return ft.Container(content=inner_card, expand=expand, alignment=ft.Alignment.CENTER)

    obj_char = ft.Container(
        content=ft.Container(
            content=char_image, bgcolor=ft.Colors.WHITE,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            border_radius=10, alignment=ft.Alignment.CENTER, padding=10, aspect_ratio=1.0
        ),
        expand=1, alignment=ft.Alignment.CENTER,
    )

    chat_text = ft.Text(
        value=random.choice(lang["home.greeting_messages"]),
        size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900, text_align=ft.TextAlign.CENTER
    )

    obj_chatbox = ft.Container(
        content=chat_text, bgcolor=ft.Colors.LIGHT_GREEN_50, padding=20,
        border_radius=ft.BorderRadius.only(top_left=20, top_right=20, bottom_left=0, bottom_right=20),
        border=ft.Border.all(2, ft.Colors.GREEN_200),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        expand=1, alignment=ft.Alignment.CENTER,
    )

    chart_data = [
        {"month": "T1", "income": 50, "expense": 40},
        {"month": "T2", "income": 65, "expense": 45},
        {"month": "T3", "income": 45, "expense": 55},
        {"month": "T4", "income": 80, "expense": 30},
        {"month": "T5", "income": 15, "expense": 65},
        {"month": "T6", "income": 85, "expense": 40},
        {"month": "T7", "income": 50, "expense": 40},
        {"month": "T8", "income": 65, "expense": 45},
        {"month": "T9", "income": 45, "expense": 55},
        {"month": "T10", "income": 80, "expense": 30},
        {"month": "T11", "income": 15, "expense": 65},
        {"month": "T12", "income": 85, "expense": 40},
    ]

    highest_val = max(max(d["income"], d["expense"]) for d in chart_data)
    max_val = highest_val if highest_val > 0 else 1

    bar_chart = fc.BarChart(
        groups=[
            fc.BarChartGroup(
                x=i,
                rods=[fc.BarChartRod(
                    from_y=0, to_y=d["income"], width=16, color=ft.Colors.WHITE,
                    gradient=ft.LinearGradient(begin=ft.Alignment.BOTTOM_CENTER, end=ft.Alignment.TOP_CENTER, colors=[ft.Colors.GREEN, ft.Colors.YELLOW]),
                    bg_to_y=max_val, bgcolor="#F0F4E6", border_radius=8,
                    tooltip=f"{lang['generic.income']}: {d['income']}\n{lang['generic.expense']}: {d['expense']}"
                )]
            ) for i, d in enumerate(chart_data)
        ],
        bottom_axis=fc.ChartAxis(
            labels=[fc.ChartAxisLabel(value=i, label=ft.Container(ft.Text(d["month"], size=12, color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD), padding=ft.Padding.only(top=10))) for i, d in enumerate(chart_data)],
            label_size=40,
        ),
        left_axis=fc.ChartAxis(
            labels=[fc.ChartAxisLabel(value=val, label=ft.Text(f"{int(val)}", size=12, color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD)) for val in range(0, int(max_val) + 10, 20)],
            label_size=40,
        ),
        horizontal_grid_lines=fc.ChartGridLines(color=ft.Colors.TRANSPARENT),
        tooltip=fc.BarChartTooltip(bgcolor=ft.Colors.BLUE_GREY_900),
        max_y=max_val, interactive=True,
    )

    line_chart = fc.LineChart(
        data_series=[fc.LineChartData(color=ft.Colors.RED, stroke_width=3, curved=False, point=True, points=[fc.LineChartDataPoint(i, d["expense"]) for i, d in enumerate(chart_data)])],
        bottom_axis=fc.ChartAxis(labels=[fc.ChartAxisLabel(value=i, label=ft.Container(ft.Text(d["month"], size=12, color=ft.Colors.TRANSPARENT, weight=ft.FontWeight.BOLD), padding=ft.Padding.only(top=10))) for i, d in enumerate(chart_data)], label_size=40),
        left_axis=fc.ChartAxis(labels=[fc.ChartAxisLabel(value=val, label=ft.Text(f"{int(val)}", size=12, color=ft.Colors.TRANSPARENT, weight=ft.FontWeight.BOLD)) for val in range(0, int(max_val) + 10, 20)], label_size=40),
        max_y=max_val,
        min_y=0,
        min_x=len(chart_data) / 60 - 1,
        max_x=len(chart_data) - len(chart_data) / 60,
        interactive=False,
    )

    chart_stack = ft.Stack(controls=[bar_chart, ft.TransparentPointer(line_chart)], expand=True)

    obj_chart = ft.Container(
        expand=True, height=320,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Row([
                            ft.Container(width=12, height=12, bgcolor=ft.Colors.GREEN, shape=ft.BoxShape.CIRCLE),
                            ft.Text(lang["generic.income"], color=ft.Colors.GREY_700, size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(width=12, height=12, bgcolor=ft.Colors.RED, shape=ft.BoxShape.CIRCLE, margin=ft.Margin(left=10, top=0, right=0, bottom=0)),
                            ft.Text(lang["generic.expense"], color=ft.Colors.GREY_700, size=14, weight=ft.FontWeight.BOLD),
                        ]),
                    ]
                ),
                ft.Container(content=chart_stack, expand=True, padding=ft.Padding.only(top=30))
            ]
        ),
        bgcolor=ft.Colors.WHITE,
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK))
    )

    total_income = float(sum(d["income"] for d in chart_data))
    total_expense = float(sum(d["expense"] for d in chart_data))
    saved_amount = total_income - total_expense
    savings_goal = 200
    saving_ratio = max(0.0, min(saved_amount / savings_goal, 1.0))
    percent_val = int(saving_ratio * 100)

    text_percent = ft.Text(f"{percent_val}%", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_900)
    text_label = ft.Text(lang["home.saving_goal"], size=12, color=ft.Colors.GREY_500, weight=ft.FontWeight.BOLD)

    gauge_chart = fc.PieChart(
        sections=[
            fc.PieChartSection(value=100, color=ft.Colors.TRANSPARENT, radius=15),
            fc.PieChartSection(value=percent_val, gradient=ft.LinearGradient(begin=ft.Alignment.BOTTOM_CENTER, end=ft.Alignment.TOP_CENTER, colors=[ft.Colors.GREEN, ft.Colors.YELLOW]), radius=30),
            fc.PieChartSection(value=100 - percent_val, color=ft.Colors.GREY_200, radius=30),
        ],
        sections_space=0,
        center_space_radius=150,
        expand=True
    )

    obj_pie = ft.Container(
        content=ft.Stack(
            controls=[
                gauge_chart,
                ft.Container(
                    content=ft.Column([text_label, text_percent], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    alignment=ft.Alignment.CENTER,
                )
            ],
            expand=True
        ),
        bgcolor=ft.Colors.WHITE, border_radius=15, padding=20,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
        expand=1,
        aspect_ratio=1.0
    )
    obj_recent_lesson = create_object("", is_square=True)

    center_container = ft.Container(
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(content=menu_button, alignment=ft.Alignment.CENTER),
                        ft.Container(content=username, expand=True, bgcolor=ft.Colors.WHITE, border_radius=10, alignment=ft.Alignment.CENTER, padding=15, shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)))
                    ]
                ),
                ft.Row(spacing=20, controls=[obj_char, obj_chatbox]),
                ft.Row(controls=[obj_chart]),
                ft.Row(spacing=20, controls=[obj_pie, obj_recent_lesson])
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
                    controls=[
                        center_container
                    ]
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
            char_image.width = safe_width * 0.9
            char_image.height = safe_width * 0.9
            new_radius = max(30, int((safe_width / 4) - 70))
            gauge_chart.center_space_radius = new_radius
            text_percent.size = max(16, int(safe_width * 0.043))
            text_label.size = max(9, int(safe_width * 0.018))
            page.update()
        except Exception:
            pass

    page.on_resize = on_page_resize
    on_page_resize(None)

    return ft.View(
        route="/home",
        padding=0,
        bgcolor=ft.Colors.WHITE,
        controls=[
            ft.Stack(
                controls=[page_content, menu],
                expand=True
            )
        ]
    )