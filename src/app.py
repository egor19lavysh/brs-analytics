from nicegui import ui

from parser import Parser


# -------------------------------------------------------------------
# Настройки
# -------------------------------------------------------------------

parser = Parser()

COURSES = [1, 2, 3, 4, 5]
ENTITIES = ['Студент', 'Группа', 'Направление']


# -------------------------------------------------------------------
# Вспомогательные функции
# -------------------------------------------------------------------

def get_year_by_course(course: int) -> int:
    """Возвращает год поступления для выбранного курса."""
    return 2026 - int(course) + 1


# -------------------------------------------------------------------
# Направления
# -------------------------------------------------------------------

def fill_directions(course_select, direction_select):
    """Заполняет список направлений в зависимости от курса."""

    def update_options():
        selected_course = course_select.value

        if selected_course is None:
            direction_select.options = {}
            direction_select.value = None
            return

        year = get_year_by_course(selected_course)
        directions = parser.get_directions(year)

        options = {
            str(direction_id): name
            for direction_id, name in directions.items()
        }

        direction_select.options = options

        if options:
            direction_select.value = next(iter(options))
        else:
            direction_select.value = None

    course_select.on_value_change(update_options)

    update_options()


# -------------------------------------------------------------------
# Группы
# -------------------------------------------------------------------

def fill_groups(course_select, direction_select, group_select):
    """Заполняет список групп."""

    def update_options():
        selected_course = course_select.value
        selected_direction = direction_select.value

        if selected_course is None or selected_direction is None:
            group_select.options = {}
            group_select.value = None
            return

        year = get_year_by_course(selected_course)

        groups = parser.get_groups(
            y=year,
            direction_id=int(selected_direction),
        )

        options = {
            str(group_id): name
            for group_id, name in groups.items()
        }

        group_select.options = options

        if options:
            group_select.value = next(iter(options))
        else:
            group_select.value = None

    course_select.on_value_change(update_options)
    direction_select.on_value_change(update_options)

    update_options()


# -------------------------------------------------------------------
# Студенты
# -------------------------------------------------------------------

def fill_students(
    course_select,
    direction_select,
    group_select,
    student_select,
):
    """Заполняет список студентов выбранной группы."""

    def update_options():
        selected_course = course_select.value
        selected_direction = direction_select.value
        selected_group = group_select.value

        if (
            selected_course is None
            or selected_direction is None
            or selected_group is None
        ):
            student_select.options = {}
            student_select.value = None
            return

        year = get_year_by_course(selected_course)

        students = parser.get_studs(
            y=year,
            direction_id=int(selected_direction),
            group_id=int(selected_group),
        )

        options = {
            str(student_id): name
            for student_id, name in students.items()
        }

        student_select.options = options

        if options:
            student_select.value = next(iter(options))
        else:
            student_select.value = None

    course_select.on_value_change(update_options)
    direction_select.on_value_change(update_options)
    group_select.on_value_change(update_options)

    update_options()


# -------------------------------------------------------------------
# Отображение селекторов
# -------------------------------------------------------------------

def setup_entity_selector(
    entity_select,
    group_select,
    student_select,
):
    """
    Настраивает отображение группы и студента
    в зависимости от выбранной сущности.
    """

    def update_visibility():
        entity = entity_select.value

        # -----------------------------------------------------------
        # Студент
        # -----------------------------------------------------------

        if entity == 'Студент':
            group_select.set_visibility(True)
            student_select.set_visibility(True)

        # -----------------------------------------------------------
        # Группа
        # -----------------------------------------------------------

        elif entity == 'Группа':
            group_select.set_visibility(True)
            student_select.set_visibility(False)

            student_select.value = None

        # -----------------------------------------------------------
        # Направление
        # -----------------------------------------------------------

        else:
            group_select.set_visibility(False)
            student_select.set_visibility(False)

            group_select.value = None
            student_select.value = None

    entity_select.on_value_change(update_visibility)

    # Начальное состояние
    update_visibility()


# -------------------------------------------------------------------
# Основной интерфейс
# -------------------------------------------------------------------

with ui.column().style(
    'min-height: 40vh; '
    'margin-left: 32.5%; '
    'justify-content: center; '
    'align-items: center;'
):

    ui.label('Что ты выберешь?').classes(
        'text-3xl font-bold mb-6'
    )

    with ui.row().classes(
        'items-center justify-center gap-8'
    ):

        # ===========================================================
        # Левая часть
        # ===========================================================

        with ui.column().classes('items-center'):

            left_entity = ui.select(
                ENTITIES,
                label='Выбор сущности',
                value='Студент',
            ).classes('w-72 text-xl')

            left_course = ui.select(
                COURSES,
                label='Курс',
                value=1,
            ).classes('w-40 mt-4 text-xl')

            left_direction = ui.select(
                {},
                label='Направление',
            ).classes('w-72 mt-4 text-xl')

            left_group = ui.select(
                {},
                label='Группа',
            ).classes('w-72 mt-4 text-xl')

            left_student = ui.select(
                {},
                label='Студент',
            ).classes('w-72 mt-4 text-xl')


        # ===========================================================
        # VS
        # ===========================================================

        ui.label('VS').classes(
            'text-4xl font-bold text-primary'
        )


        # ===========================================================
        # Правая часть
        # ===========================================================

        with ui.column().classes('items-center'):

            right_entity = ui.select(
                ENTITIES,
                label='Выбор сущности',
                value='Группа',
            ).classes('w-72 text-xl')

            right_course = ui.select(
                COURSES,
                label='Курс',
                value=2,
            ).classes('w-40 mt-4 text-xl')

            right_direction = ui.select(
                {},
                label='Направление',
            ).classes('w-72 mt-4 text-xl')

            right_group = ui.select(
                {},
                label='Группа',
            ).classes('w-72 mt-4 text-xl')

            right_student = ui.select(
                {},
                label='Студент',
            ).classes('w-72 mt-4 text-xl')


# -------------------------------------------------------------------
# Заполнение направлений
# -------------------------------------------------------------------

fill_directions(
    left_course,
    left_direction,
)

fill_directions(
    right_course,
    right_direction,
)


# -------------------------------------------------------------------
# Заполнение групп
# -------------------------------------------------------------------

fill_groups(
    left_course,
    left_direction,
    left_group,
)

fill_groups(
    right_course,
    right_direction,
    right_group,
)


# -------------------------------------------------------------------
# Заполнение студентов
# -------------------------------------------------------------------

fill_students(
    left_course,
    left_direction,
    left_group,
    left_student,
)

fill_students(
    right_course,
    right_direction,
    right_group,
    right_student,
)


# -------------------------------------------------------------------
# Настройка отображения
# -------------------------------------------------------------------

setup_entity_selector(
    left_entity,
    left_group,
    left_student,
)

setup_entity_selector(
    right_entity,
    right_group,
    right_student,
)


# -------------------------------------------------------------------
# Запуск
# -------------------------------------------------------------------

ui.run()
