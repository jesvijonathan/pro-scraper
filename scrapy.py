from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import jsonify
import json
import time
import threading
import chromedriver
from logger import logger
import config
import hashlib
import re
from database import getDb

json_format_1 = {
    "title": None,
    "tags": None,
    "price": None,
    "other_price": None,
    "market": None,
    "shipping": None,
    "price_description": None,
    "additional_info": None,
    "rating": {
        "score": None,
        "reviews": None
    },
    "img": None,
    "link": None,
    "other_links": None,
    "hash": None,
    "scraped": None,
    "last_scraped": None,
    "verified": None,
    "in_stock": None
}


class GoogleScrapy:

    def __init__(self, product):
        self.rproduct = product
        self.product = product.replace(" ", "+")
        self.url = f"https://www.google.com/search?q={self.product}&tbm=shop"
        self.driver = chromedriver.get_chromedriver()
        self.page_source = None
        self.product_data = []

        if self.driver:
            logger.info("Got chromedriver instance")
        else:
            logger.error("Failed to get chromedriver instance")

    def __del__(self):
        chromedriver.release_chromedriver(self.driver)

    def scrap_product_data_db(self):
        con = getDb()
        keywords = self.rproduct.split(" ")
        sql = "SELECT * FROM products WHERE " + " AND ".join(["title LIKE %s"] * len(keywords))
        params = ["%" + keyword + "%" for keyword in keywords]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchall()
        con.cursor.close()
        con.close()

        if len(result) == 0:
            self.scrape_product_data()
            return self.product_data

        json_parsed = []

        for index, row in enumerate(result):
            if index > config.max_quick_search_results:
                break
            tmp = json_format_1.copy()
            tmp["additional_info"] = row[14]
            tmp["hash"] = row[2]
            tmp["img"] = row[4]
            tmp["in_stock"] = row[11]
            tmp["last_scraped"] = row[18]
            tmp["link"] = row[10]
            tmp["market"] = row[5]
            tmp["other_links"] = row[16].split(" ")
            tmp["other_price"] = row[7]
            tmp["price"] = row[6]
            tmp["price_description"] = row[15]
            tmp["rating"] = {
                "reviews": row[8],
                "score": row[9]
            }
            tmp["scraped"] = row[17]
            tmp["shipping"] = row[3]
            tmp["tags"] = [tag for tag in row[1].split(" ") if tag.isalnum()]
            tmp["title"] = row[1]
            tmp["verified"] = row[12]
            json_parsed.append(tmp)

        return json_parsed

    def scrape_product_data(self):
        self.driver.get(self.url)
        self.page_source = WebDriverWait(self.driver, config.webload_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sh-dgr__content")))
        self.products = self.driver.find_elements(By.CLASS_NAME, "sh-dgr__content")

        for index, product in enumerate(self.products):
            if index > config.max_search_results:
                break

            tmp = json_format_1.copy()
            divs = product.find_elements(By.TAG_NAME, "div")
            imgs = product.find_elements(By.TAG_NAME, "img")
            links = product.find_elements(By.TAG_NAME, "a")

            for div in divs:
                class_name = div.get_attribute("class")
                raw_text = div.text
                rtext = raw_text.strip()
                text = rtext.encode("ascii", "ignore").decode("utf-8")

                if class_name == "EI11Pd":
                    tmp["title"] = text
                    tmp["tags"] = text.replace("(", "").replace(")", "").replace("[", "").replace("]", "").replace("{", "").replace("}", "").replace("<", "").replace(">", "").replace(",", "").split(" ")
                    tmp["tags"] = [tag for tag in tmp["tags"] if tag.isalnum()]
                elif class_name == "XrAfOe":
                    price = rtext.split("\n")[0]
                    price = price.replace("₹", "").replace(",", "").replace("$", "").replace("Rs."," ")
                    price = re.findall(r'\d+\.\d+|\d+', price)
                    price = [float(value) for value in price]
                    
                    if(len(price) ==2):
                        tmp["price"] = price[0]
                        tmp["other_price"] = price[1]
                    elif len(price) == 1: 
                        tmp["price"] = price[0]
                elif class_name == "aULzUe IuHnof":
                    tmp["market"] = text
                elif class_name == "bONr3b":
                    tmp["shipping"] = text
                elif class_name == "zLPF4b":
                    tmp["price_description"] = text
                elif class_name == "dWRflb":
                    tmp["additional_info"] = text
                elif class_name == "NzUzee":
                    rating_parts = text.split("\n")
                    tmp["rating"] = {
                        "score": rating_parts[0],
                        "reviews": rating_parts[1].replace(",", "") if len(rating_parts) >= 2 else None
                    }

            tmp["img"] = imgs[0].get_attribute("src") if imgs else None
            link_list = []
            last_link = None

            for link in links:
                ll = link.get_attribute("href")

                if ll is not None and (last_link is None or ll[:100] != last_link[:100]):
                    link_list.append(ll)

                last_link = ll

            if len(link_list) > 1:
                tmp["link"] = link_list[1]
                link_list[0], link_list[1] = link_list[1], link_list[0]
            else:
                tmp["link"] = link_list[0]

            tmp["other_links"] = link_list

            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            tmp["scraped"] = current_time
            tmp["last_scraped"] = current_time
            tmp["verified"] = False
            tmp["in_stock"] = ""

            hash_string = tmp["img"] if tmp["img"] else tmp["title"]
            tmp["hash"] = hashlib.md5(hash_string.encode()).hexdigest()

            self.product_data.append(tmp)

        con = getDb()

        sql = """INSERT INTO products (
    title,
    hash,
    img,
    market,
    shipping,
    price,
    other_price,
    reviews,
    score,
    link,
    in_stock,
    verified,
    tags,
    additional_info,
    price_description,
    other_links,
    scraped,
    last_scraped
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s, %s) 
ON DUPLICATE KEY UPDATE last_scraped=VALUES(last_scraped), price=VALUES(price), shipping=VALUES(shipping), title=VALUES(title), in_stock=VALUES(in_stock), additional_info=VALUES(additional_info), tags=VALUES(tags), img=VALUES(img), price_description=VALUES(price_description), reviews=VALUES(reviews), score=VALUES(score), verified=VALUES(verified), other_links=VALUES(other_links)
"""
        val = []

        for product in self.product_data:
            for key, value in product.items():
                if value is None:
                    product[key] = None
                    
            reviews = product["rating"]["reviews"]
            score = product["rating"]["score"] 
        
            if reviews is not None and reviews.isdigit():
                reviews = int(reviews)
            else:
                reviews = -1
        
            if score is not None and score.replace(".", "").isdigit():
                score = float(score)
            else:
                score = -1.0

            tags = ' '.join(str(tag) for tag in product["tags"]) if product["tags"] is not None else ''


            other_links = ' '.join(product["other_links"])
            val.append(
                (product["title"], product["hash"], product["img"], product["market"], product["shipping"],
                 product["price"], product["other_price"], reviews, score, product["link"], product["in_stock"],
                 product["verified"], tags, product["additional_info"], product["price_description"], other_links,
                 product["scraped"], product["last_scraped"]))

        con.cursor.executemany(sql, val)
        con.db.commit()

        logger.info(f"Successfully inserted {len(self.product_data)} products into the database")

        return self.product_data

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
