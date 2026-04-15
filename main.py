import flet as ft
import src.app as app
import os

if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    assets = os.path.join(curr_dir, "assets")

    ft.run(app.main, assets_dir=assets)