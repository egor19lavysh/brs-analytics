import curl_cffi
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from datetime import date
import pandas as pd
import re




class Parser:

    def __init__(self,
                 url: str = "https://rating.unecon.ru/"):
        self.base_url = url
        self.ua = UserAgent()

    def _get_soup(self, url: str) -> BeautifulSoup | None:
        try:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://rating.unecon.ru/',
            }
            response = curl_cffi.get(url=url, headers=headers, impersonate='chrome')
            response.raise_for_status()
            return BeautifulSoup(response.content, features="html.parser")
        except Exception as e:
            print(e)
            return None


    def get_directions(self, y: int) -> dict[int, str]:
        url = f"{self.base_url}?y={y}"
        soup = self._get_soup(url=url)

        li_tag = soup.find('div', class_='filter').find_all('li')[3]

        field = li_tag.find('b')

        directions = {}

        if field and field.text.lower().strip() == 'направление':
            options = li_tag.find('div', class_='options').find_all('a', class_='option nowrap_ellipsis')

            for option in options[1:]:
                href = option.get('href')

                if not href:
                    continue

                direction_match = re.search(r"[?&]up=([^&]+)", href)

                if direction_match:
                    direction_id = int(direction_match.group(1).split('=')[-1])
                    directions[direction_id] = option.get_text(strip=True)

        return directions

    def get_groups(self, y: int, direction_id: int) -> dict[int, str]:
        url = f"{self.base_url}?y={y}&up={direction_id}"
        soup = self._get_soup(url=url)

        filter_tag = soup.find('div', class_='filter')

        li_tag = filter_tag.find_all('li')[5] if filter_tag else None

        field = li_tag.find('b')

        groups = {}

        if field and field.text.lower().strip() == 'группа':
            options = li_tag.find('div', class_='options').find_all('a', class_='option nowrap_ellipsis')

            for option in options:
                href = option.get('href')

                if option.get_text(strip=True) in ('Все группы', "Не выбрано"):
                    continue

                if not href:
                    continue

                group_match = re.search(r"[?&]g=([^&]+)", href)

                if group_match:
                    group_id = int(group_match.group(1).split('=')[-1])
                    groups[group_id] = option.get_text(strip=True)

        return groups

    def get_studs(self, y: int, direction_id: int, group_id: int) -> dict[int, str]:
        url = f"{self.base_url}?y={y}&up={direction_id}&g={group_id}"
        soup = self._get_soup(url=url)

        studs = {}

        body = soup.find('table').find('tbody')
        for tr in body.find_all('tr'):
            td = tr.find('td', class_='align_left')
            a_tag = td.find('a')

            if a_tag:
                href = a_tag.get('href')
                stud_id_match = re.search(r"[?&]stud=([^&]+)", href)

                if stud_id_match:
                    stud_id = int(stud_id_match.group(1).split('=')[-1])
                    studs[stud_id] = a_tag.get_text(strip=True)

        return studs

            

    def get_direction_rating_table(self, y: int,
                                    direction_id: int,
                                    s: int = 1) -> pd.DataFrame:
        url = f"{self.base_url}?y={y}&up={direction_id}&s={s}"
        soup = self._get_soup(url=url)

        data={
            "Фамилия, имя, отчество": [],
            "Группа": [],
        }

        table = soup.find('table')

        thead = table.find('thead')

        lessons = thead.find_all('tr')[1].find_all('th')

        for lesson in lessons:
            lesson_name = lesson.get('title').replace(" (Зачет)", "").replace(" (Экзамен)", "").replace(" (дифф.зач.)", "")
            data[lesson_name] = []

        data["Сумма баллов"] = []

        df = pd.DataFrame(data)

        tbody = table.find('tbody')

        students = tbody.find_all('tr')

        for student in students:
            row = [td.get_text(strip=True) for td in student.find_all('td')[1:]]
            df.loc[len(df)] = row

        score_columns = df.columns[2:]
        df[score_columns] = df[score_columns].apply(pd.to_numeric, errors="coerce")

        df = df.drop(columns=["Сумма баллов"])

        df = df.set_index("Фамилия, имя, отчество")

        return df

    def get_direction_rating_tables(self, y: int, direction_id: int) -> pd.DataFrame:

        curr_year = date.today().year
        diff = curr_year - y
        all_semesters = diff * 2 + 1

        dfs = []

        for s in range(1, all_semesters + 1):
            df = self.get_direction_rating_table(y=y, direction_id=direction_id, s=s)

            dfs.append(df)

        result_df = pd.concat(dfs, axis=1)

        return result_df

    @staticmethod
    def _normalize_score(value: str | None) -> float | int | None:
        if value is None:
            return None

        cleaned = str(value).strip().replace(' ', '').replace(',', '.')
        if cleaned in {'', '-', '–'}:
            return None

        try:
            number = float(cleaned)
        except ValueError:
            return None

        if number.is_integer():
            return int(number)
        return number

    @staticmethod
    def _parse_subject_name(raw_text: str) -> str:
        text = re.sub(r'\s+', ' ', raw_text).strip()
        if 'Форма контроля:' in text:
            text = text.split('Форма контроля:', 1)[0].strip()

        match = re.search(r'(.*?\([^)]*\))', text)
        if match:
            return match.group(1).strip()

        return text

    @staticmethod
    def _parse_form_control(raw_text: str) -> str:
        if 'Форма контроля:' not in raw_text:
            return ''

        text = raw_text.split('Форма контроля:', 1)[1]
        match = re.search(r'([^КТ]*?)(?:\s+КТ\s*\d+\s*:|$)', text)
        if match:
            return match.group(1).strip()
        return text.strip()

    def _parse_stud_rating_table(self, table) -> pd.DataFrame:
        records = []
        current_semester = None

        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if not cells:
                continue

            first_cell_text = cells[0].get_text(' ', strip=True)

            if re.fullmatch(r'\d+\s+семестр', first_cell_text):
                current_semester = first_cell_text
                continue

            if first_cell_text.startswith('Предмет и форма контроля'):
                continue

            if len(cells) < 8:
                continue

            subject_name = self._parse_subject_name(first_cell_text)
            form_control = self._parse_form_control(first_cell_text)
            points = [self._normalize_score(cell.get_text(' ', strip=True)) for cell in cells[1:5]]

            record = {
                'Семестр': current_semester,
                'Предмет': subject_name.replace(' (Зачет)', '').replace(' (Экзамен)', '').replace(' (Дифференцированный зачет)', ''),
                'Форма контроля': form_control,
                'КТ 1': points[0],
                'КТ 2': points[1],
                'КТ 3': points[2],
                'КТ 4': points[3],
                'Баллы за экзамен': self._normalize_score(cells[5].get_text(' ', strip=True)),
                'Сумма баллов': self._normalize_score(cells[6].get_text(' ', strip=True)),
                'Оценка': cells[7].get_text(' ', strip=True) or None,
            }
            records.append(record)

        return pd.DataFrame.from_records(records)

    def get_stud_rating(self, stud_id: int) -> pd.DataFrame:
        url = f"{self.base_url}stud_cd.php?stud={stud_id}"
        soup = self._get_soup(url=url)

        if soup is None:
            return pd.DataFrame()

        table = soup.find('table', class_='stud_cds')
        if table is None:
            return pd.DataFrame()

        return self._parse_stud_rating_table(table)




if __name__ == "__main__":
    parser = Parser()

    dirs = parser.get_studs(y=2024, direction_id=13788, group_id=13707)
    print(dirs)
    

