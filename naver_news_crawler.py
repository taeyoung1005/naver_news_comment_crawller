from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os
import chromedriver_autoinstaller
from multiprocessing import Process, Manager, cpu_count, freeze_support
from datetime import datetime, timedelta
import numpy as np
from openpyxl import Workbook
import csv

chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
driver_path = f'./{chrome_ver}/chromedriver.exe'
if os.path.exists(driver_path) != True:
    print("크롬버전에 맞는 크롬드라이버 설치중...")
    chromedriver_autoinstaller.install(True)
    print("크롬드라이버 설치완료")

def crawl_links(search, start_date, end_date, url_list):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
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

def crawl_comment(url_list, comment_list):

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
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

    for url in url_list:
        driver.get("https://n.news.naver.com/mnews/article/comment/" + url.split('article/')[-1])
        sleep(2)
        if "entertain" in driver.current_url or "sports" in driver.current_url:
            continue
        
        try:
            if driver.find_element(By.CLASS_NAME, 'u_cbox_count').text == '0':
                continue

            driver.find_element(By.CLASS_NAME, 'u_cbox_cleanbot_setbutton').click()
            if driver.find_element(By.CLASS_NAME, 'u_cbox_layer_cleanbot2_checkbox.is_checked').is_displayed() == True:
                driver.find_element(By.ID, 'cleanbot_dialog_checkbox_cbox_module').click()
            driver.find_element(By.CLASS_NAME, 'u_cbox_layer_cleanbot2_extrabtn').click()
            sleep(2)
        except:
            continue

        #댓글 전체보기
        # print("댓글 전체보기")
        while True:
            if driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more').is_displayed() == True:
                driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more').click()
                # print("더보기 클릭")
                sleep(1)
            else:
                # print("더보기 없음")
                break

        #댓글 가져오기
        # print("댓글 가져오기")
        cboxs = driver.find_elements(By.CLASS_NAME, 'u_cbox_comment_box.u_cbox_type_profile')
        cboxs = [i for i in cboxs if "u_cbox_type_delete" not in i.get_attribute('class')]
        # print(f"cboxs : len {len(cboxs)}")
        for cbox in cboxs:
            try:
                title = driver.find_element(By.CLASS_NAME, 'media_end_head_headline').text
                date = cbox.find_element(By.CLASS_NAME, 'u_cbox_date').text.split(' ')[0]
                comment = cbox.find_element(By.CLASS_NAME, 'u_cbox_contents').text
                comment_list.append([title, date, comment])
                print(f'{title} - {date} : {comment}')
            except:
                pass
        # print("기사 끝")

if __name__ == '__main__':
    freeze_support()

    num_of_cpu = int(cpu_count()*0.8)
    manager = Manager()
    url_list = manager.list()
    comment_list = manager.list()

    search = "월드컵"
    start_date = "20221120"
    end_date= "20221203"

    sd = start_date
    ed = end_date

    start_date = datetime.strptime(start_date, "%Y%m%d")
    end_date = datetime.strptime(end_date, "%Y%m%d")

    ##############################링크수집##############################
    date_list = [(start_date + timedelta(days=i)).strftime("%Y%m%d") for i in range((end_date-start_date).days+1)]
    if len(date_list) < num_of_cpu:
        link_crawl_cpu = len(date_list)
    else:
        link_crawl_cpu = num_of_cpu
    date_list = np.array_split(date_list, link_crawl_cpu)
    date_list = [x.tolist() for x in date_list]

    processes = []

    for i in range(link_crawl_cpu):
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

    ##############################댓글 수집##############################
    with open(f'./{search}_{sd}_{ed}/{search}_{sd}_{ed}_url.txt', 'r', encoding='utf-8') as f:
        url_list = f.readlines()
    url_list = np.array_split(url_list, num_of_cpu)
    url_list = [x.tolist() for x in url_list]

    processes = []
    for i in range(num_of_cpu):
        process = Process(target=crawl_comment,
            args=(
                url_list[i],
                comment_list
            )
        )
        
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    with open(f'./{search}_{sd}_{ed}/{search}_{sd}_{ed}_comment.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(comment_list)

    wb = Workbook()
    ws = wb.active
    with open(f'./{search}_{sd}_{ed}/{search}_{sd}_{ed}_comment.csv', 'r', encoding='utf8') as f:
        for row in csv.reader(f):
            ws.append(row)
    wb.save(f'./{search}_{sd}_{ed}/{search}_{sd}_{ed}_comment.xlsx')