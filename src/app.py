from nicegui import ui
from datetime import date
from parser import Parser


def parse():
    parser = Parser()

    a.text = parser.get_directions(int(selector.value)).__str__()

    

years = [2026, 2025, 2024, 2023]
selector = ui.select(options=years, label="Выберите год поступления", on_change=parse)

a = ui.label('')

ui.run()