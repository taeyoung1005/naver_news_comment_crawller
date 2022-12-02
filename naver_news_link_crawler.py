from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import chromedriver_autoinstaller
from multiprocessing import Process, Manager, cpu_count, freeze_support
from datetime import datetime, timedelta
import numpy as np

chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path) != True:
    print("크롬버전에 맞는 크롬드라이버 설치중...")
    chromedriver_autoinstaller.install(True)
    print("크롬드라이버 설치완료")

def crawl_links(search, start_date, end_date, url_list):

    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--privileged')
    chrome_options.add_argument('--incognito')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('window-size=1920x1080')
    chrome_options.add_argument('disable-gpu')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36")
    chrome_options.add_argument('lang=ko_KR')
    chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])

    driver = webdriver.Chrome(driver_path, options=chrome_options)

    url = f"https://search.naver.com/search.naver?where=news&query={search}&sm=tab_opt&sort=0&photo=0&field=0&pd=3&ds={start_date}&de={end_date}&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Ar%2Cp%3Afrom{start_date}to{end_date}&is_sug_officeid=0"

    driver.get(url)

    def gather_url():
        try:
            info_list = driver.find_elements(By.CLASS_NAME, 'info')
            for info in info_list:
                if info.get_attribute('href') != None:
                    url = info.get_attribute('href')
                    if "news.naver.com" in url and "sports" not in url and "entertain" not in url:
                        url_list.append(url)
                        print(f'{url}')
        except:
            pass
    while True:
        gather_url()
        try:
            if driver.find_element(By.CLASS_NAME, 'btn_next').is_displayed() == True and driver.find_element(By.CLASS_NAME, 'btn_next').get_attribute('aria-disabled') == 'false':
                driver.find_element(By.CLASS_NAME, 'btn_next').click()
            else:
                break
        except:
            break
    driver.quit()

if __name__ == '__main__':
    freeze_support()

    num_of_cpu = int(cpu_count()*0.8)
    manager = Manager()
    url_list = manager.list()

    search = "윤석열"
    start_date = "20221120"
    end_date= "20221201"

    sd = start_date
    ed = end_date

    start_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    date_list = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range((end_date-start_date).days+1)]
    date_list = np.array_split(date_list, num_of_cpu)
    date_list = [x.tolist() for x in date_list]

    processes = []
    for i in range(num_of_cpu):
        process = Process(target=crawl_links,
            args=(
                search,
                date_list[i][0],
                date_list[i][-1],
                url_list
            )
        )
        
        processes.append(process)
        process.start()
        

    for process in processes:
        process.join()

    url_list = list(set(url_list))
    if not os.path.exists(f'./{search}_{sd}_{ed}'):
        os.makedirs(f'./{search}_{sd}_{ed}')
    with open(f'./{search}_{sd}_{ed}/{search}_{sd}_{ed}_url.txt', 'w', encoding='utf-8') as f:
        for i in url_list:
            print(i)
            f.write(i+'\n')