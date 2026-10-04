from nicegui import ui
import pandas as pd
import numpy as np
from app import parser
from visual import *



_dashboard_data = None


def set_dashboard_data(
    first_entity,
    first_name,
    second_entity,
    second_name,
    first_data,
    second_data,
):
    global _dashboard_data

    _dashboard_data = {
        'first_entity': first_entity,
        'second_entity': second_entity,
        'first_data': first_data,
        'second_data': second_data,
        'first_name': first_name,
        'second_name': second_name,
    }

# Вспомогательные функции

def _collect_subjects(first_data, second_data) -> list[str]:
    subjects = set()

    for df in (first_data, second_data):
        if 'Предмет' in df.columns:
            subjects.update(df['Предмет'].dropna().unique().tolist())
        else:
            subjects.update(c for c in df.columns if c != 'Группа')

    return ['Все предметы'] + sorted(subjects)


def _filter_by_subject(df, subject: str):
    if subject == 'Все предметы':
        return df

    if 'Предмет' in df.columns:
        return df[df['Предмет'] == subject]

    #оставляем столбец группу (если есть) + выбранный предмет
    keep_cols = ['Группа'] if 'Группа' in df.columns else []
    if subject in df.columns:
        keep_cols.append(subject)

    return df[keep_cols]

# Функции сравнения

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

    plots.append(
            plot_mean_score(
                first_name,
                second_name,
                first_data['Сумма баллов'].dropna().mean(),
                second_data['Сумма баллов'].dropna().mean(),
            )
        )
    

    return plots


def compare_group_group(
    first_data,
    second_data,
    first_name='Группа 1',
    second_name='Группа 2',
):

    plots = []

    first_subjects = first_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()
    second_subjects = second_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()

    # Столбчатая по предметам
    plots.append(
        plot_bars(first_name, second_name, first_subjects, second_subjects)
    )

    # Radar профилей
    plots.append(
        plot_radar(first_name, second_name, first_subjects, second_subjects)
    )

    # Dumbbell разрыва по предметам
    plots.append(
        plot_dumbbell(first_name, second_name, first_subjects, second_subjects)
    )

    # Box plot средних баллов студентов
    first_stud_avg = first_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    second_stud_avg = second_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    plots.append(
        plot_box(first_name, second_name, first_stud_avg, second_stud_avg)
    )

    return plots


def compare_direction_direction(
    first_data,
    second_data,
    first_name='Направление 1',
    second_name='Направление 2',
):

    plots = []

    first_subjects = first_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()
    second_subjects = second_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()

    # Столбчатая по предметам
    plots.append(
        plot_bars(first_name, second_name, first_subjects, second_subjects)
    )

    #  Dumbbell разрыва
    plots.append(
        plot_dumbbell(first_name, second_name, first_subjects, second_subjects)
    )

    # Radar профилей
    plots.append(
        plot_radar(first_name, second_name, first_subjects, second_subjects)
    )

    # Гистограмма распределения средних баллов студентов
    first_stud_avg = first_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    second_stud_avg = second_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    plots.append(
        plot_histogram(first_name, second_name, first_stud_avg, second_stud_avg)
    )

    return plots


def compare_student_group(
    first_data,
    second_data,
    first_name='Студент',
    second_name='Группа',
):

    plots = []

    first_subjects = (
        first_data[['Предмет', 'Сумма баллов']]
        .dropna(subset=['Сумма баллов'])
        .groupby('Предмет')['Сумма баллов']
        .mean()
        .to_dict()
    )

    second_subjects = (
        second_data.drop(columns=['Группа'], errors='ignore')
        .mean(numeric_only=True)
        .to_dict()
    )

    # Dumbbell: студент vs средний балл группы по предметам
    plots.append(
        plot_dumbbell(first_name, second_name, first_subjects, second_subjects)
    )

    # Radar профиля студента и группы
    plots.append(
        plot_radar(first_name, second_name, first_subjects, second_subjects)
    )

    # Box plot: балл студента на фоне распределения студентов группы
    student_scores = first_data['Сумма баллов'].dropna().tolist()
    group_stud_avg = second_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    plots.append(
        plot_box(first_name, second_name, student_scores, group_stud_avg)
    )

    # Гистограмма: баллы студента vs средние баллы студентов группы
    plots.append(
        plot_histogram(first_name, second_name, student_scores, group_stud_avg)
    )

    return plots


def compare_student_direction(
    first_data,
    second_data,
    first_name='Студент',
    second_name='Направление',
):

    plots = []

    first_subjects = (
        first_data[['Предмет', 'Сумма баллов']]
        .dropna(subset=['Сумма баллов'])
        .groupby('Предмет')['Сумма баллов']
        .mean()
        .to_dict()
    )

    second_subjects = (
        second_data.drop(columns=['Группа'], errors='ignore')
        .mean(numeric_only=True)
        .to_dict()
    )

    plots.append(
        plot_bars(first_name, second_name, first_subjects, second_subjects)
    )

    # Dumbbell разрыва по предметам
    plots.append(
        plot_dumbbell(first_name, second_name, first_subjects, second_subjects)
    )

    # Box plot: балл студента на фоне распределения по направлению
    student_scores = first_data['Сумма баллов'].dropna().tolist()
    direction_stud_avg = second_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    plots.append(
        plot_box(first_name, second_name, student_scores, direction_stud_avg)
    )

    # Гистограмма распределения
    plots.append(
        plot_histogram(first_name, second_name, student_scores, direction_stud_avg)
    )

    return plots


def compare_group_direction(
    first_data,
    second_data,
    first_name='Группа',
    second_name='Направление',
):

    plots = []

    first_subjects = first_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()
    second_subjects = second_data.drop(columns=['Группа'], errors='ignore').mean(numeric_only=True).to_dict()

    # Столбчатая по предметам
    plots.append(
        plot_bars(first_name, second_name, first_subjects, second_subjects)
    )

    # где группа отрывается/отстаёт от направления
    plots.append(
        plot_dumbbell(first_name, second_name, first_subjects, second_subjects)
    )

    # Box plot средних баллов студентов группы vs направления
    first_stud_avg = first_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    second_stud_avg = second_data.drop(columns=['Группа'], errors='ignore').mean(axis=1, numeric_only=True).tolist()
    plots.append(
        plot_box(first_name, second_name, first_stud_avg, second_stud_avg)
    )

    # Гистограмма распределения средних баллов студентов
    plots.append(
        plot_histogram(first_name, second_name, first_stud_avg, second_stud_avg)
    )

    return plots

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
    first_name = _dashboard_data.get('first_name', '')
    second_name = _dashboard_data.get('second_name', '')


    ui.label(
        f'Сравнение: {first_name} — {second_name}'
    ).classes('text-2xl font-bold')

    # Выбор функции сравнения
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

    compare_function = functions.get((first_entity, second_entity))

    if compare_function is None:
        ui.label('Для такого типа сравнения функция пока не реализована')
        return

    # Селектор предметов + контейнер для графиков
    subjects = _collect_subjects(first_data, second_data)

    selected_subject = {'value': subjects[0]}

    plots_container = ui.column().classes('w-full')

    def rebuild_plots():
        plots_container.clear()

        filtered_first = _filter_by_subject(first_data, selected_subject['value'])
        filtered_second = _filter_by_subject(second_data, selected_subject['value'])

        with plots_container:
            figures = compare_function(
                filtered_first,
                filtered_second,
                first_name or first_entity,
                second_name or second_entity,
            )
            for figure in figures:
                ui.plotly(figure).classes('w-full h-[600px]')

    ui.select(
        options=subjects,
        value=subjects[0],
        label='Предмет',
        with_input=True,
        on_change=lambda e: (
            selected_subject.update({'value': e.value}),
            rebuild_plots(),
        ),
    ).classes('w-80')

    # Первичная отрисовка
    rebuild_plots()

    ui.button(
        '← Назад',
        on_click=lambda: ui.navigate.to('/'),
    ).classes('mt-4')