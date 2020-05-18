import scrapy
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
# import pymongo
import pymysql

class Book(scrapy.Spider):
    name = 'bookstore'
    start_urls = ['https://www.books.com.tw/']

    def __init__(self):
        #連接PyMySQL
        self.db = pymysql.connect("localhost", "root", "0inglanne", "bookdb")
        self.cursor = self.db.cursor()
        #無頭模式自動操作網頁
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
    
    def parse(self, response):
        key = input("輸入要爬取的商品:")
        page = int(input('爬取頁數:'))
        self.driver.get(response.url)
        time.sleep(2)
        buttonclose = self.driver.find_element_by_class_name('close')
        buttonclose.click()
        time.sleep(2)

        text = self.driver.find_element_by_id('key')
        text.send_keys(key)
        print('輸入完成')
        button = self.driver.find_element_by_xpath('//div[@class="search clearfix"]/form/button')
        button.click()
        print('Enter')
        time.sleep(3)

        c_tab = "INSERT INTO store02 (書名, 價錢, 出版, 簡介) VALUES (%s, %s, %s, %s)"
        self.cursor.execute("CREATE TABLE store02 (id INT AUTO_INCREMENT PRIMARY KEY, 書名 VARCHAR(255), 價錢 VARCHAR(255), 出版 VARCHAR(255), 簡介 VARCHAR(255))")

        #爬取相應頁數並寫入數據庫
        for i in range(page):
            r_list = self.driver.find_elements_by_xpath('//ul[@class="searchbook"]//li')
            xList = []
            # titleList = ['書名', '價錢', '出版', '簡介']
            for r in r_list:
                # print(r.text)
                m = r.text.split('\n')
                # print(m)
                commit = m[3]
                name = m[0]
                price = m[2]
                if len(price) < 25:
                    price = price[:-6]
                else :
                    price = price[:-9]
                market = m[1]
                L = [name.strip(),price.strip(),market.strip(), commit.strip()]
                # L = [name.strip(),price.strip()]
                L = tuple(L)
                # print(L)
                xList.append(L)
            # print(xList)
            self.cursor.executemany(c_tab, xList)
            self.db.commit()

            button = self.driver.find_element_by_class_name('nxt')
            button.click()
            time.sleep(2)
        self.driver.quit()
