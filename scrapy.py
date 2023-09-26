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



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from flask import Response
from flask import jsonify
import json
import threading
import chromedriver
from logger import logger
import config
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        self.product = product.replace(" ", "+")
        self.url = f"https://www.google.com/search?q={self.product}&tbm=shop"
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
        self.page_source = WebDriverWait(self.driver, config.webload_timeout).until(EC.presence_of_element_located((By.CLASS_NAME, "sh-dgr__content")))
        self.products = self.driver.find_elements(By.CLASS_NAME, "sh-dgr__content")
 
        for index, product in enumerate(self.products):
            if (index > config.max_search_results):
                break
            
            tmp = {}
            divs = product.find_elements(By.TAG_NAME, "div")
            imgs = product.find_elements(By.TAG_NAME, "img")
            links = product.find_elements(By.TAG_NAME, "a")
            for div in divs:
                class_name = div.get_attribute("class")
                raw_text = div.text 
                text = raw_text.strip()
                if class_name == "EI11Pd":
                    tmp["title"] = text
                    tmp["tags"] = text.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("<", "").replace(">", "").replace(",", "").split(" ")
                elif class_name == "XrAfOe":
                    tmp["price"] = text.split("\n")[0].encode("ascii", "ignore").decode("utf-8").replace(",", "")
                elif class_name == "aULzUe IuHnof":
                    tmp["market"] = div.text
                elif class_name == "bONr3b":
                    tmp["shipping"] = text
                elif class_name == "zLPF4b":
                    tmp["price_description"] = text
                elif class_name == "dWRflb":
                    tmp["additional_info"] = text.encode("ascii", "ignore").decode("utf-8")
                elif class_name == "NzUzee":
                    rating_parts = text.split("\n")
                    score = rating_parts[0] or 0
                    reviews = rating_parts[1].replace(",", "") or 0
                    
                    tmp["rating"] = {"score": score, "reviews": reviews}
            
            tmp["img"] = imgs[0].get_attribute("src") if imgs else None
            link_list = []
            last_link = None

            for link in links:
                ll = link.get_attribute("href")

                if ll is not None and (last_link is None or ll[:100] != last_link[:100]):
                    link_list.append(ll)

                last_link = ll

            if len(link_list) > 1:
                link_list[0], link_list[1] = link_list[1], link_list[0]

            tmp["links"] = link_list
            # link_list = []
            # last_link = None
            # for link in links:
            #     ll = link.get_attribute("href")
            #     # if first 100 character of link is same as last link, skip
            #     if last_link != None and ll != None:
            #         if ll[:100] == last_link[:100]:
            #             continue
            #     if ll != None:
            #         link_list.append(ll)
            #     last_link = ll
            # if len(link_list) > 1:
            #     tmp_link = link_list[0]
            #     link_list[0] = link_list[1]
            #     link_list[1] = tmp_link
            # tmp["links"] = link_list
            current_time = time.time()
            tmp["scraped"] = current_time
            tmp["last_scraped"] = current_time
            tmp["verified"] = False
            tmp["in_stock"] = ""



            self.product_data.append(tmp)

        return (self.product_data)
        # for index, product in enumerate(self.products):
        #     if (index > config.max_search_results):
        #         break
        #     tmp = {}
        #     divs = product.find_elements(By.TAG_NAME, "div")
        #     imgs = product.find_elements(By.TAG_NAME, "img")
        #     links = product.find_elements(By.TAG_NAME, "a")
        #     for div in divs:
        #         if div.get_attribute("class") == "EI11Pd":
        #             tmp["title"] = div.text
        #         elif div.get_attribute("class") == "sh-dgr__content":
        #             tmp["price"] = div.text
        #     for img in imgs:
        #         tmp["img"] = img.get_attribute("src")
        #     for link in links:
        #         tmp["link"] = link.get_attribute("href")
        #     self.product_data.append(tmp)
        return self.products


    def parse(self, response):
        self.products = self.driver.find_elements(
            By.CLASS_NAME, "sh-dgr__grid-result")
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



                # i0X6df : All Descriptopn Text
               
               ## EI11Pd : Title
               
               ## NzUzee : Rating
                #        : Number of Ratings
                #        : Out of & Summary
                
                # dWRflb : additional info
                
                # zLPF4b : Price description
                #        : price
                #        : store
                #        : shipping

               ## XrAfOe : price & mrp
               
               ## IuHnof : store 
                # aULzUe : store
               
               ## bONr3b : shipping


 


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
