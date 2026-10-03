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