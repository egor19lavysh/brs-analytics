from nicegui import ui
import pandas as pd
import numpy as np
from visual import *


# Данные текущего анализа
_dashboard_data = None


def set_dashboard_data(
    first_entity,
    second_entity,
    first_data,
    second_data,
):
    global _dashboard_data

    _dashboard_data = {
        'first_entity': first_entity,
        'second_entity': second_entity,
        'first_data': first_data,
        'second_data': second_data,
    }


# ============================================================
# Функции сравнения
# ============================================================

def compare_student_student(
    first_data,
    second_data,
    first_name='Студент 1',
    second_name='Студент 2',
):

    plots = []

    df1 = first_data[['Предмет', 'Сумма баллов']].set_index('Предмет')
    df2 = second_data[['Предмет', 'Сумма баллов']].set_index('Предмет')

    first_averages = df1['Сумма баллов'].to_dict()
    second_averages = df2['Сумма баллов'].to_dict()

    plots.append(
        plot_bars(
            first_name,
            second_name,
            first_averages,
            second_averages,
        )
    )

    plots.append(
        plot_number_lists(
            first_name,
            second_name,
            first_data.groupby('Семестр')['Сумма баллов'].mean().tolist(),
            second_data.groupby('Семестр')['Сумма баллов'].mean().tolist(),
        )
    )

    common_subjects = np.intersect1d(first_data['Предмет'], second_data['Предмет'])
    plots.append(
            plot_horizontal_bar(
                {subject: first_averages[subject] - second_averages[subject] for subject in common_subjects},
                first_name,
                second_name
            )
        )
    

    return plots


def compare_group_group(
    first_data,
    second_data,
    first_name='Группа 1',
    second_name='Группа 2',
):
    pass


def compare_direction_direction(
    first_data,
    second_data,
    first_name='Направление 1',
    second_name='Направление 2',
):
    pass


def compare_student_group(
    first_data,
    second_data,
    first_name='Студент',
    second_name='Группа',
):
    pass


def compare_student_direction(
    first_data,
    second_data,
    first_name='Студент',
    second_name='Направление',
):
    pass


def compare_group_direction(
    first_data,
    second_data,
    first_name='Группа',
    second_name='Направление',
):
    pass

# ============================================================
# Dashboard
# ============================================================

@ui.page('/dashboard')
def dashboard_page():

    if _dashboard_data is None:
        ui.label('Нет данных для анализа')
        ui.link('Вернуться назад', '/')
        return

    first_entity = _dashboard_data['first_entity']
    second_entity = _dashboard_data['second_entity']

    first_data = _dashboard_data['first_data']
    second_data = _dashboard_data['second_data']

    ui.label(
        f'Сравнение: {first_entity} — {second_entity}'
    ).classes('text-2xl font-bold')

    # --------------------------------------------------------
    # Выбираем функцию сравнения
    # --------------------------------------------------------

    functions = {
        ('Студент', 'Студент'): compare_student_student,
        ('Группа', 'Группа'): compare_group_group,
        ('Направление', 'Направление'): compare_direction_direction,

        ('Студент', 'Группа'): compare_student_group,
        ('Группа', 'Студент'): compare_student_group,

        ('Студент', 'Направление'): compare_student_direction,
        ('Направление', 'Студент'): compare_student_direction,

        ('Группа', 'Направление'): compare_group_direction,
        ('Направление', 'Группа'): compare_group_direction,
    }

    compare_function = functions.get(
        (first_entity, second_entity)
    )

    if compare_function is None:
        ui.label(
            'Для такого типа сравнения функция пока не реализована'
        )
        return

    # --------------------------------------------------------
    # Строим график
    # --------------------------------------------------------

    figures = compare_function(
        first_data,
        second_data,
        first_entity,
        second_entity,
    )

    for figure in figures:
        ui.plotly(figure).classes('w-full h-[600px]')

    ui.button(
        '← Назад',
        on_click=lambda: ui.navigate.to('/'),
    ).classes('mt-4')