from collections.abc import Mapping, Sequence
import numpy as np
import plotly.graph_objects as go


def plot_number_lists(
    first_name: str,
    second_name: str,
    first_values: Sequence[int | float],
    second_values: Sequence[int | float],
) -> go.Figure:
    """Build a line chart comparing two numeric lists by element index."""
    figure = go.Figure()
    figure.add_scatter(
        name=first_name,
        x=list(range(1, len(first_values) + 1)),
        y=first_values,
        mode="lines+markers",
    )
    figure.add_scatter(
        name=second_name,
        x=list(range(1, len(second_values) + 1)),
        y=second_values,
        mode="lines+markers",
    )
    figure.update_layout(
        title="Сравнение списков чисел",
        xaxis_title="Средний балл",
        yaxis_title="Семестр",
    )
    return figure


def plot_bars(
    first_name: str,
    second_name: str,
    first_averages: Mapping[str, float],
    second_averages: Mapping[str, float],
) -> go.Figure:
    """Build a grouped bar chart for subjects shared by both mappings."""
    subjects = [
        subject
        for subject in first_averages
        if subject in second_averages
    ]

    figure = go.Figure()
    figure.add_bar(
        name=first_name,
        x=subjects,
        y=[first_averages[subject] for subject in subjects],
    )
    figure.add_bar(
        name=second_name,
        x=subjects,
        y=[second_averages[subject] for subject in subjects],
    )
    figure.update_layout(
        title="Сравнение баллов по общим предметам",
        xaxis_title="Предмет",
        yaxis_title="Сумма баллов",
        barmode="group",
    )

    if not subjects:
        figure.add_annotation(
            text="Нет общих предметов",
            showarrow=False,
        )

    return figure

def plot_horizontal_bar(
    values: dict[str, float],
    first_name: str,
    second_name: str
) -> go.Figure:

    figure = go.Figure()
    figure.add_bar(
        name=f"Разница между {first_name} и {second_name}",
        x=np.array(list(values.values())),
        y=list(values.keys()),
        orientation="h"
    )
    return figure

def plot_box(
    first_name: str,
    second_name: str,
    first_values: Sequence[int | float],
    second_values: Sequence[int | float],
) -> go.Figure:
    """Box plot для сравнения распределения двух наборов значений."""
    figure = go.Figure()
    figure.add_box(
        name=first_name,
        y=list(first_values),
        boxmean=True,
    )
    figure.add_box(
        name=second_name,
        y=list(second_values),
        boxmean=True,
    )
    figure.update_layout(
        title="Сравнение распределения баллов",
        yaxis_title="Баллы",
    )
    return figure


def plot_radar(
    first_name: str,
    second_name: str,
    first_averages: Mapping[str, float],
    second_averages: Mapping[str, float],
) -> go.Figure:
    """Radar chart по общим предметам двух сущностей."""
    subjects = [
        subject
        for subject in first_averages
        if subject in second_averages
    ]

    figure = go.Figure()

    if subjects:
        figure.add_trace(go.Scatterpolar(
            r=[first_averages[s] for s in subjects],
            theta=subjects,
            fill='toself',
            name=first_name,
        ))
        figure.add_trace(go.Scatterpolar(
            r=[second_averages[s] for s in subjects],
            theta=subjects,
            fill='toself',
            name=second_name,
        ))

    figure.update_layout(
        title="Профиль по предметам (radar)",
        polar=dict(radialaxis=dict(visible=True)),
    )

    if not subjects:
        figure.add_annotation(text="Нет общих предметов", showarrow=False)

    return figure


def plot_dumbbell(
    first_name: str,
    second_name: str,
    first_averages: Mapping[str, float],
    second_averages: Mapping[str, float],
) -> go.Figure:
    """Dumbbell chart: линия между двумя точками по каждому предмету."""
    subjects = [
        subject
        for subject in first_averages
        if subject in second_averages
    ]

    figure = go.Figure()

    if subjects:
        first_vals = [first_averages[s] for s in subjects]
        second_vals = [second_averages[s] for s in subjects]

        # Соединительные линии
        for subject, fv, sv in zip(subjects, first_vals, second_vals):
            figure.add_trace(go.Scatter(
                x=[fv, sv],
                y=[subject, subject],
                mode='lines',
                line=dict(color='lightgray', width=3),
                showlegend=False,
                hoverinfo='skip',
            ))

        # Точки первой сущности
        figure.add_trace(go.Scatter(
            x=first_vals,
            y=subjects,
            mode='markers',
            marker=dict(size=12),
            name=first_name,
        ))

        # Точки второй сущности
        figure.add_trace(go.Scatter(
            x=second_vals,
            y=subjects,
            mode='markers',
            marker=dict(size=12),
            name=second_name,
        ))

    figure.update_layout(
        title="Dumbbell: разрыв по предметам",
        xaxis_title="Баллы",
        yaxis_title="Предмет",
    )

    if not subjects:
        figure.add_annotation(text="Нет общих предметов", showarrow=False)

    return figure


def plot_histogram(
    first_name: str,
    second_name: str,
    first_values: Sequence[int | float],
    second_values: Sequence[int | float],
) -> go.Figure:
    """Наложенная гистограмма распределения баллов."""
    figure = go.Figure()
    figure.add_histogram(
        name=first_name,
        x=list(first_values),
        opacity=0.6,
    )
    figure.add_histogram(
        name=second_name,
        x=list(second_values),
        opacity=0.6,
    )
    figure.update_layout(
        title="Распределение баллов (гистограмма)",
        xaxis_title="Баллы",
        yaxis_title="Количество",
        barmode='overlay',
    )
    return figure


def plot_sorted_bars(
    values: Mapping[str, float],
    name: str,
) -> go.Figure:
    """Односущностная сортированная столбчатая диаграмма."""
    sorted_items = sorted(values.items(), key=lambda x: x[1], reverse=True)
    subjects = [k for k, _ in sorted_items]
    scores = [v for _, v in sorted_items]

    figure = go.Figure()
    figure.add_bar(
        x=subjects,
        y=scores,
        name=name,
    )
    figure.update_layout(
        title=f"Рейтинг предметов: {name}",
        xaxis_title="Предмет",
        yaxis_title="Баллы",
    )
    return figure