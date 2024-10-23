import os

from bs4 import BeautifulSoup
import requests, lxml, csv
from time import sleep
import threading
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


# Заголовки для запросов
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
}

# Адрес сайта
site_url = 'https://lms.samgups.ru/'

# Имя csv файла
filename = 'samgups.csv'

def parser_to_csv(min_index: int, max_index: int):

    # Контекстная переменная session
    with requests.Session() as session:
        cookie_name = os.environ.get('COOKIE_MOODLE_SESSION_NAME')
        cookie_value = os.environ.get('COOKIE_MOODLE_SESSION_VALUE')
        # Добавляем куки авторизованной сессии
        session.cookies.set(name=cookie_name, value=cookie_value)

        # Цикл для пробега по всем возможным страницам пользователей
        for user_index in range(min_index, max_index):
            # Адрес пользователя
            user_url = f"{site_url}blocks/sibportfolio/index.php?userid={user_index}"
            # Get запрос по адресу пользователя и получение ответа
            response = session.get(url=user_url, headers=headers)
            # Объект BeautifulSoup
            user_soup = BeautifulSoup(response.text, "lxml")

            try:
                # Поиск ошибки
                danger_text = user_soup.find(
                    name='span',
                    attrs={"id": "maincontent"}
                ).find_next_sibling(
                    name='div',
                    class_='alert'
                ).text
                continue
            except:
                pass
                # Логирование пользователей
                # print("User -", user_index)

            try:
                # Фио пользователя
                user_last_first_second_names = user_soup.find(
                    name='div',
                    class_='block_sibportfolio_profile'
                ).find(name='div').find('b').text.strip()
            except:
                # Фио пользователя при ошибке
                user_last_first_second_names = ''

            try:
                # table блок
                table_block = user_soup.find(
                    name='div',
                    class_='block_sibportfolio_wrapper'
                ).find(name='table', class_='table')
            except:
                # table блок при ошибке
                table_block = None

            try:
                # tr блоки
                tr_blocks = table_block.find_all(name='tr')
            except:
                # tr блоки при ошибке
                tr_blocks = None

            try:
                # Номера групп пользователя в списке
                user_groups = table_block.find_all(name='th', class_='block_sibportfolio_gray')
            except:
                # Номера групп пользователя в списке при ошибке
                user_groups = []

            # Номера групп пользователя строкой
            user_groups_str = ""
            try:
                # Цикл номеров групп пользователя
                for user_group in user_groups:
                    # Производим канкатенацию текста к user_groups_str
                    user_groups_str += user_group.find(
                        name='span',
                        class_='block_sibportfolio_helptext'
                    ).text + ";"
            except:
                pass

            def get_string_of_i_tags(index: int) -> str:
                user_str = ""
                try:
                    user_list = tr_blocks[index].find_all(name='i')
                    for user_element in user_list:
                        user_str += user_element.text + ";"
                except:
                    pass
                return user_str

            # Номера зачетных книжек пользователя
            user_books_numbers_str = get_string_of_i_tags(1)
            # Профиля подготовки пользователя
            user_profile_direction = get_string_of_i_tags(2)
            # Формы обучения пользователя
            user_education_form = get_string_of_i_tags(3)

            # Строка с данными пользователя
            user_row = (
                user_url,
                user_last_first_second_names,
                user_groups_str,
                user_books_numbers_str,
                user_profile_direction,
                user_education_form,
            )

            try:
                # Открываем csv файл для добавления данных
                with open(filename, 'a', newline='', encoding='utf-8') as file:
                    filewriter = csv.writer(file, delimiter=';')

                    filewriter.writerow(user_row)
            except:
                # Печатаем ошибку записи пользователя
                print('[ERROR] ---RECORD---: User -', user_index)

            # Останавливаем выполнения дальнейших команд на 0.01 секунду
            sleep(0.01)



def call_threads(threads_count: int, list_length: int):
    threads = []
    thread_list_length = list_length // threads_count
    for i in range(threads_count):
        min_index = int(i * thread_list_length)
        if i == threads_count - 1:
            max_index = list_length
        else:
            max_index = int(min_index + thread_list_length)

        thread = threading.Thread(target=parser_to_csv, args=(min_index, max_index))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("\n\n--------------|Работа полностью выполнена|--------------\n\n")


def write_columns_names_csv(do_it=False):
    if do_it:
        # Открываем csv файл для записи данных
        with open(filename, 'w+', newline='', encoding='utf-8') as file:
            filewriter = csv.writer(file, delimiter=';')

            row = (
                'Ссылка',
                'ФИО',
                'Номер группы',
                'Номер зачетной книжки',
                'Профиль подготовки',
                'Форма обучения',
            )
            filewriter.writerow(row)


if __name__ == '__main__':
    write_columns_names_csv(do_it=True)
    time_before = datetime.now()
    call_threads(threads_count=12, list_length=1000000)
    time_after = datetime.now()
    print("Общее время выполнения кода =", time_after - time_before)

