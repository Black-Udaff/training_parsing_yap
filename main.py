import re
import requests_cache
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm
from constants import BASE_DIR, MAIN_DOC_URL


def whats_new():
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    session = requests_cache.CachedSession()
    response = session.get(whats_new_url)
    response.encoding = 'utf-8'
    # Создание "супа".
    soup = BeautifulSoup(response.text, features='lxml')

    # Шаг 1-й: поиск в "супе" тега section с нужным id. Парсеру нужен только 
    # первый элемент, поэтому используется метод find().
    main_div = soup.find('section', attrs={'id': 'what-s-new-in-python'})

    # Шаг 2-й: поиск внутри main_div следующего тега div с классом toctree-wrapper.
    # Здесь тоже нужен только первый элемент, используется метод find().
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})

    # Шаг 3-й: поиск внутри div_with_ul всех элементов списка li с классом toctree-l1.
    # Нужны все теги, поэтому используется метод find_all().
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})

    # Печать первого найденного элемента.
    results = []
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = soup.find('h1')
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ')
        # Добавьте в список ссылки и текст из тегов h1 и dl в виде кортежа.
        results.append(
            (version_link, h1.text, dl_text)
        )

    # Печать списка с данными.
    for row in results:
        # Распаковка каждого кортежа при печати при помощи звездочки.
        print(*row)

def latest_versions():
    session = requests_cache.CachedSession()
    response = session.get(MAIN_DOC_URL)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = soup.find('div', class_='sphinxsidebarwrapper')
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
    # Проверка, есть ли искомый текст в содержимом тега.
        if 'All versions' in ul.text:
            # Если текст найден, ищутся все теги <a> в этом списке.
            a_tags = ul.find_all('a')
            # Остановка перебора списков.
            break
    # Если нужный список не нашёлся,
    # вызывается исключение и выполнение программы прерывается.
    else:
        raise Exception('Ничего не нашлось')
    results = []
    # Шаблон для поиска версии и статуса:
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    # Цикл для перебора тегов <a>, полученных ранее.
    for a_tag in a_tags:
        # Напишите новый код, ориентируясь на план.
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:  
            # Если строка соответствует паттерну,
            # переменным присываивается содержимое групп, начиная с первой.
            version, status = text_match.groups()
        else:  
            # Если строка не соответствует паттерну,
            # первой переменной присваивается весь текст, второй — пустая строка.
            version, status = a_tag.text, ''  
        # Добавление полученных переменных в список в виде кортежа.
        results.append(
            (link, version, status)
        )
    # Печать результата.
    for row in results:
        print(*row) 

def download():
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    session = requests_cache.CachedSession()
    response = session.get(downloads_url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, features='lxml')
    table_tag = soup.find('table', class_='docutils')
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
# Получите полную ссылку с помощью функции urljoin.
    archive_url = urljoin(downloads_url, pdf_a4_link) 
    print(archive_url)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    # Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
    # Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    # В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content) 
    