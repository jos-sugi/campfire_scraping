import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Constants
BASE_URL = 'https://camp-fire.jp/projects'
MAX_PAGE = 3

def init_webdriver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920x1080')
    return webdriver.Chrome(options=options)

def extract_number_from_script(script_text):
    return re.findall(r'/projects/(\d+)', script_text)[0] if script_text else None

def extract_number_from_href(href):
    match = re.search(r'/projects/view/(\d+)', href)
    return match.group(1) if match else None

def print_project_details(soup_detail):
    labels = soup_detail.find_all('label', class_='project-name')
    print('タイトル: ', labels[0].text if labels else 'N/A')

    # ノーオペレーション ラムダ関数を定義
    noop = lambda x: x

    divs_to_extract = [
        ('strong', 'another-default', '支援総額', noop),
        ('span', 'target tb-none sp-none', '目標金額', lambda x: x.replace('JPY', '')),
        ('strong', 'patron inner', '支援人数', noop),
        ('strong', 'rest inner', 'ステータス', noop)
    ]

    for tag, class_name, label, transform_func in divs_to_extract:
        divs = soup_detail.find_all('div', class_=class_name)
        print(divs)
        for div in divs:
            # 目標金額のときのみspanあとは
            value = div.find(tag)
            text = value.text if value else None
            
            print(f'{label}: ', transform_func(value.text) if value else 'N/A')

def process_page(driver, page_number):
    url = f'{BASE_URL}?page={page_number}&project_status%5B%5D=closed'
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    container = soup.find('div', class_='container')
    if not container:
        print("containerクラスが見つかりません")
        return

    boxes = container.select('.boxes4 .box')
    for box in boxes:
        box_thumbnail = box.find('div', class_='box-thumbnail')
        if not box_thumbnail:
            print("box-thumbnailクラスが見つかりません")
            continue

        script_tag = box_thumbnail.find('script')
        number = extract_number_from_script(script_tag.string) if script_tag else None

        if not number:
            for a_tag in box_thumbnail.find_all('a', href=True):
                number = extract_number_from_href(a_tag['href'])
                if number:
                    break

        if number:
            detail_driver = init_webdriver()
            detail_driver.get(f'{BASE_URL}/{number}')
            print_project_details(BeautifulSoup(detail_driver.page_source, 'html.parser'))
            detail_driver.quit()
        else:
            print("Project number not found")

def main():
    driver = init_webdriver()
    for i in range(MAX_PAGE):
        process_page(driver, i)
    driver.quit()

if __name__ == '__main__':
    main()
