from nicegui import ui
from datetime import date
from parser import Parser
from plotly import graph_objects as go


with ui.column().style('min-height: 40vh; margin-left: 32.5%; justify-content: center; align-items: center;'):
    ui.label('Что ты выберешь?').classes('text-3xl font-bold mb-6')

    with ui.row().classes('items-center justify-center gap-8'):
        with ui.column().classes('items-center'):
            ui.select(
                ['Студент', 'Группа', 'Направление'],
                label='Выбор сущности',
                value='Студент'
            ).classes('w-72 text-xl')
            ui.select(
                [1, 2, 3, 4, 5],
                label='Курс',
                value=1
            ).classes('w-40 mt-4 text-xl')

        ui.label('VS').classes('text-4xl font-bold text-primary')

        with ui.column().classes('items-center'):
            ui.select(
                ['Студент', 'Группа', 'Направление'],
                label='Выбор сущности',
                value='Группа'
            ).classes('w-72 text-xl')
            ui.select(
                [1, 2, 3, 4, 5],
                label='Курс',
                value=2
            ).classes('w-40 mt-4 text-xl')


ui.run()