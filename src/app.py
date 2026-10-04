from nicegui import ui

from parser import Parser
from redis_cache import RedisClient
import dashboard


COURSES = [1, 2, 3, 4, 5]
ENTITIES = ['Студент', 'Группа', 'Направление']


def get_year_by_course(course: int) -> int:
    return 2026 - course + 1


parser = Parser(cache=RedisClient())


def get_comparison_function(first_entity: str, second_entity: str):
    functions = {
        ('Студент', 'Студент'): dashboard.compare_student_student,
        ('Группа', 'Группа'): dashboard.compare_group_group,
        ('Направление', 'Направление'): dashboard.compare_direction_direction,

        ('Студент', 'Группа'): dashboard.compare_student_group,
        ('Группа', 'Студент'): dashboard.compare_student_group,

        ('Студент', 'Направление'): dashboard.compare_student_direction,
        ('Направление', 'Студент'): dashboard.compare_student_direction,

        ('Группа', 'Направление'): dashboard.compare_group_direction,
        ('Направление', 'Группа'): dashboard.compare_group_direction,
    }

    return functions.get((first_entity, second_entity))


def get_rating_data(
    entity: str,
    course: int,
    direction_id: int | None = None,
    group_id: int | None = None,
    student_id: int | None = None,
):
    year = get_year_by_course(course)

    if entity == 'Студент':
        return parser.get_stud_rating(student_id)

    if entity == 'Группа':
        df = parser.get_direction_rating_tables(
            y=year,
            direction_id=direction_id,
        )

        group_name = parser.get_groups(
            y=year,
            direction_id=direction_id,
        )[group_id]

        group_column = next(
            (
                column_index
                for column_index, column_name in enumerate(df.columns)
                if column_name == 'Группа'
            ),
            None,
        )
        if group_column is None:
            raise KeyError('В таблице рейтинга отсутствует колонка «Группа»')

        group_values = df.iloc[:, group_column]
        return df.iloc[group_values.eq(group_name).to_numpy()]

    if entity == 'Направление':
        return parser.get_direction_rating_tables(
            y=year,
            direction_id=direction_id,
        )

    return None


@ui.page('/')
def index():

    ui.label('БРС.Аналитика').classes('text-2xl font-bold')

    with ui.row().classes('w-full'):


        with ui.column().classes('w-1/2'):
            ui.label('Первая сущность')

            first_course = ui.select(
                COURSES,
                label='Курс',
                value=4,
            ).classes('w-full')

            first_entity = ui.select(
                ENTITIES,
                label='Тип сущности',
                value='Студент',
            ).classes('w-full')

            first_direction = ui.select(
                options={},
                label='Направление',
            ).classes('w-full')

            first_group = ui.select(
                options={},
                label='Группа',
            ).classes('w-full')

            first_student = ui.select(
                options={},
                label='Студент',
            ).classes('w-full')

        # Правая сущность

        with ui.column().classes('w-1/2'):
            ui.label('Вторая сущность')

            second_course = ui.select(
                COURSES,
                label='Курс',
                value=4,
            ).classes('w-full')

            second_entity = ui.select(
                ENTITIES,
                label='Тип сущности',
                value='Студент',
            ).classes('w-full')

            second_direction = ui.select(
                options={},
                label='Направление',
            ).classes('w-full')

            second_group = ui.select(
                options={},
                label='Группа',
            ).classes('w-full')

            second_student = ui.select(
                options={},
                label='Студент',
            ).classes('w-full')

    # Заполнение направлений

    def update_first_directions():
        year = get_year_by_course(first_course.value)

        directions = parser.get_directions(year)

        first_direction.options = directions
        first_direction.value = None
        first_direction.update()

    def update_second_directions():
        year = get_year_by_course(second_course.value)

        directions = parser.get_directions(year)

        second_direction.options = directions
        second_direction.value = None
        second_direction.update()

    # Группы

    def update_first_groups():
        if first_direction.value is None:
            return

        year = get_year_by_course(first_course.value)

        groups = parser.get_groups(
            year,
            first_direction.value,
        )

        first_group.options = groups
        first_group.value = None
        first_group.update()

    def update_second_groups():
        if second_direction.value is None:
            return

        year = get_year_by_course(second_course.value)

        groups = parser.get_groups(
            year,
            second_direction.value,
        )

        second_group.options = groups
        second_group.value = None
        second_group.update()

    # Студенты

    def update_first_students():
        if first_direction.value is None or first_group.value is None:
            return

        year = get_year_by_course(first_course.value)

        students = parser.get_studs(
            year,
            first_direction.value,
            first_group.value,
        )

        first_student.options = students
        first_student.value = None
        first_student.update()

    def update_second_students():
        if second_direction.value is None or second_group.value is None:
            return

        year = get_year_by_course(second_course.value)

        students = parser.get_studs(
            year,
            second_direction.value,
            second_group.value,
        )

        second_student.options = students
        second_student.value = None
        second_student.update()


    def update_first_visibility():
        entity = first_entity.value

        first_direction.set_visibility(
            entity in ('Студент', 'Группа', 'Направление')
        )

        first_group.set_visibility(
            entity in ('Студент', 'Группа')
        )

        first_student.set_visibility(
            entity == 'Студент'
        )

    def update_second_visibility():
        entity = second_entity.value

        second_direction.set_visibility(
            entity in ('Студент', 'Группа', 'Направление')
        )

        second_group.set_visibility(
            entity in ('Студент', 'Группа')
        )

        second_student.set_visibility(
            entity == 'Студент'
        )

    first_entity.on_value_change(update_first_visibility)
    second_entity.on_value_change(update_second_visibility)

    first_course.on_value_change(update_first_directions)
    second_course.on_value_change(update_second_directions)

    first_direction.on_value_change(update_first_groups)
    second_direction.on_value_change(update_second_groups)

    first_group.on_value_change(update_first_students)
    second_group.on_value_change(update_second_students)

    update_first_directions()
    update_second_directions()

    update_first_visibility()
    update_second_visibility()

    # Запуск анализа

    def run_analysis():

        first_data = get_rating_data(
            entity=first_entity.value,
            course=first_course.value,
            direction_id=first_direction.value,
            group_id=first_group.value,
            student_id=first_student.value,
        )

        second_data = get_rating_data(
            entity=second_entity.value,
            course=second_course.value,
            direction_id=second_direction.value,
            group_id=second_group.value,
            student_id=second_student.value,
        )

        compare_function = get_comparison_function(
            first_entity.value,
            second_entity.value,
        )

        if compare_function is None:
            ui.notify(
                'Такое сравнение пока не реализовано',
                type='warning',
            )
            return

        if first_entity.value == 'Студент':
            first_ops = first_student.options
            first_entity_id = first_student.value
        elif first_entity.value == 'Направление':
            first_ops = first_direction.options
            first_entity_id = first_direction.value
        elif first_entity.value == 'Группа':
            first_ops = first_group.options
            first_entity_id = first_group.value

        if second_entity.value == 'Студент':
            second_ops = second_student.options
            second_entity_id = second_student.value
        elif second_entity.value == 'Направление':
            second_ops = second_direction.options
            second_entity_id = second_direction.value
        elif second_entity.value == 'Группа':
            second_ops = second_group.options
            second_entity_id = second_group.value

        dashboard.set_dashboard_data(
            first_entity=first_entity.value,
            first_name=first_ops[first_entity_id] if first_entity_id is not None else str(first_entity.value),
            second_entity=second_entity.value,
            second_name=second_ops[second_entity_id] if second_entity_id is not None else str(second_entity.value),
            first_data=first_data,
            second_data=second_data,
        )

        ui.navigate.to('/dashboard')

    ui.button(
        'Запустить анализ',
        on_click=run_analysis,
    ).classes('mt-6')


ui.run()