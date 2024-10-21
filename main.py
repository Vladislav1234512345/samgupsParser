from bs4 import BeautifulSoup
import lxml, requests, csv

# Заголовки для запросов
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
}

# Адрес сайта
site_url = 'https://lms.samgups.ru/'

filename = 'samgups.csv'

with requests.Session() as session:
    session.cookies.set(name="MoodleSession", value="g56scoeip5em5810kb4jv8lv46")

    for user_index in range(100000):

        user_url = f"{site_url}blocks/sibportfolio/index.php?userid={user_index}"

        response = session.get(url=user_url, headers=headers)



        break

