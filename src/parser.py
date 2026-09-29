import curl_cffi
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import re



class Parser:

    def __init__(self,
                 url: str = "https://rating.unecon.ru/"):
        self.url = url
        self.ua = UserAgent()

    def _get_soup(self, url: str) -> BeautifulSoup | None:
        try:
            headers = {'User-Agent': self.ua.random}
            reponse = curl_cffi.get(url=url, headers=headers)
        except Exception as e:
            print(e)
        
        reponse.raise_for_status()
        
        return BeautifulSoup(reponse.content)


    def get_directions(self, year: int) -> dict[int, str]:
        url = f"{self.url}?y={year}"
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



if __name__ == "__main__":
    parser = Parser()

    dirs = parser.get_directions(year=2023)
    

