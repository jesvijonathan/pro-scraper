from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from flask import jsonify
import json
import threading
import chromedriver
from logger import logger
import config
# product = input("product:")
# product = product.replace(" ", "+")
# url = "https://www.google.com/search?q=" + product + "&tbm=shop"

# options = webdriver.ChromeOptions()
# options.add_argument("--headless") 

# driver = webdriver.Chrome(executable_path="C:\chromedriver.exe", options=options)
# driver.get(url)

# def scrape_product_data():
#     product_data = []
    
#     products = driver.find_elements(By.CLASS_NAME, "sh-dgr__grid-result")

#     for product in products:
#         tmp = {}
        
#         divs = product.find_elements(By.TAG_NAME, "div")
#         imgs = product.find_elements(By.TAG_NAME, "img")
#         links = product.find_elements(By.TAG_NAME, "a")
        
#         print("\n#################\n")
#         # print(divs)
#         for div in divs:
#             # print(div.get_attribute("class"))            
#             print(div.text)
#             # print(div.get_attribute("class"))
#             # if div.get_attribute("class") == "EI11Pd":
#             # if div.get_attribute("class") == "sh-dgr__content":
#             #     print(div.text)
#             #     time.sleep(0.1)
#         for img in imgs:
#             print(img.get_attribute("src"))
#         for link in links:
#             print(link.get_attribute("href"))
        
#         product_data.append(tmp)
#     return product_data

# product_data = scrape_product_data()

# driver.quit()


# class scrapyProduct():
#     def __init__(self, product):
#         self.product = product
#         self.product = self.product.replace(" ", "+")
#         self.url = "https://www.google.com/search?q=" + self.product + "&tbm=shop"
        
        
#     def scrape_product_data(self):
#         product_data = []
#         for product in self.products:
#             tmp = {}
#             divs = product.find_elements(By.TAG_NAME, "div")
#             imgs = product.find_elements(By.TAG_NAME, "img")
#             links = product.find_elements(By.TAG_NAME, "a")
#             for div in divs:
#                 if div.get_attribute("class") == "EI11Pd":
#                     tmp["title"] = div.text
#                 elif div.get_attribute("class") == "sh-dgr__content":
#                     tmp["price"] = div.text
#             for img in imgs:
#                 tmp["img"] = img.get_attribute("src")
#             for link in links:
#                 tmp["link"] = link.get_attribute("href")
#             product_data.append(tmp)
#         return product_data


class GoogleScrapy():

    def __init__(self, product):
        self.product = product
        self.product = self.product.replace(" ", "+")
        self.url = "https://www.google.com/search?q=" + self.product + "&tbm=shop"
        self.driver = chromedriver.get_chromedriver()
        self.page_source = None
        self.product_data = []
        self.products = None

        if self.driver: 
            logger.info("Got chromedriver instance")
        else:
            logger.error("Failed to get chromedriver instance")
            return None
    
    def __del__(self):
        chromedriver.release_chromedriver(self.driver)

    def scrape_product_data(self): 
        # try:
            # self.page_source = self.driver.get(self.url)
            # self.parse(self.page_source)
            # return self.product_data
        # except Exception as e:
        #     logger.error("Failed scrapping product data | " + str(e)) 
        #     return None
        # finally:    
            # self.__del__()
        self.driver.get(self.url)

        products = self.driver.find_elements(By.CLASS_NAME, "sh-dgr__grid-result")

        for index, product in enumerate(products):
            if(index >config.max_search_results):
                break
            tmp = {}
        
            divs = product.find_elements(By.TAG_NAME, "div")
            imgs = product.find_elements(By.TAG_NAME, "img")
            links = product.find_elements(By.TAG_NAME, "a")
        
            # print("\n#################\n")
            # print(divs)

            tmp["text"] = []
            for div in divs:
                # print(div.get_attribute("class"))            
                # print(div.text)
                # print(div.get_attribute("class"))
                # if div.get_attribute("class") == "EI11Pd":
                if div.get_attribute("class") == "sh-dgr__content":
                #     print(div.text)
                      tmp["text"].append(div.text)
                #     time.sleep(0.1)
            tmp["img"] = [] 
            for img in imgs:
                # print(img.get_attribute("src"))
                # tmp["img"].append("<img src='"+img.get_attribute("src")+"'>")
                tmp["img"].append(img.get_attribute("src"))
            tmp["link"] = []
            for link in links:
                # print(link.get_attribute("href"))
                tmp["link"].append(link.get_attribute("href"))
        
            self.product_data.append(tmp)
        # print(self.product_data)
        return json.dumps(self.product_data)
  

    def parse(self, response):
        self.products = self.driver.find_elements(By.CLASS_NAME, "sh-dgr__grid-result")
        for product in self.products:
            tmp = {}
            divs = product.find_elements(By.TAG_NAME, "div")
            imgs = product.find_elements(By.TAG_NAME, "img")
            links = product.find_elements(By.TAG_NAME, "a")
            for div in divs:
                if div.get_attribute("class") == "EI11Pd":
                    tmp["title"] = div.text
                elif div.get_attribute("class") == "sh-dgr__content":
                    tmp["price"] = div.text
            for img in imgs:
                tmp["img"] = img.get_attribute("src")
            for link in links:
                tmp["link"] = link.get_attribute("href")
            self.product_data.append(tmp)
        return self.product_data

def scrap(product):
    product = product.replace(" ", "+")
    url = "https://www.google.com/search?q=" + product + "&tbm=shop"
    driver = chromedriver.get_chromedriver()
    if driver:
        try:
            driver.get(url)
            return driver.page_source
        finally:
            chromedriver.release_chromedriver(driver)   
    else:
        logger.error("Failed to get chromedriver instance")
        return None
    
    
