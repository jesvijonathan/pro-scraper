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
        self.hash = product
        self.product = product.replace(" ", "+")
        self.url = f"https://www.google.com/search?q={self.product}&tbm=shop"
        self.driver = chromedriver.get_chromedriver()
        self.page_source = None
        self.product_data = []

        self.con = getDb()
        self.main_link = None

        if self.driver:
            logger.info("Got chromedriver instance")
        else:
            logger.error("Failed to get chromedriver instance")

    def __del__(self):
        self.con.close()
        chromedriver.release_chromedriver(self.driver)

    def scrap_product(self, deep=False):

        con = self.con

        sql = "SELECT * FROM products WHERE hash = %s"
        params = [self.hash]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchone()


        if result is None:
            return jsonify({"error": "Product hash not found in products, try deep search"}), 404
        
        json_parsed = json_format_1.copy()
        json_parsed["additional_info"] = result[14]
        json_parsed["hash"] = result[2]
        json_parsed["img"] = result[4]
        json_parsed["in_stock"] = result[11]
        json_parsed["last_scraped"] = result[18]
        json_parsed["link"] = result[10]
        json_parsed["market"] = result[5]
        json_parsed["other_links"] = result[16].split(" ")
        json_parsed["other_price"] = result[7]
        json_parsed["price"] = result[6]
        json_parsed["price_description"] = result[15]
        json_parsed["rating"] = {
            "reviews": result[8],
            "score": result[9]
        }
        json_parsed["scraped"] = result[17]
        json_parsed["shipping"] = result[3]
        if result[1] is not None:
            json_parsed["tags"] = [tag for tag in result[1].split(" ") if tag.isalnum()]
            json_parsed["title"] = result[1]
        else:
            json_parsed["tags"] = None
            json_parsed["title"] = result[2]
        json_parsed["verified"] = result[12]


        try:
            self.main_link = json_parsed["other_links"][1]
        except:
            return jsonify({"error": "Product hash not found in products, try deep search"}, json_parsed), 404
        
        if deep:
            result = self.scrap_product_link_deep()
        else:
            result = self.scrap_product_link_db()

        return result
    
    def ref_product(self):
        con = self.con

        sql = "SELECT * FROM products WHERE hash = %s"
        params = [self.hash]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchone()

        if result is None:
            return jsonify({"error": "Product hash not found in products, try deep search"}), 404
        
        try:
            other_l = result[16].split(" ")
            self.main_link = other_l[1]
            self.hash = result[2]
            resp = self.scrap_product_link_deep()
            return resp

        except:
            return jsonify({"error": "Error while deep scraping reviews"}), 404


    
        
    def scrap_product_link_db(self):
        con = self.con

        sql = "SELECT * FROM product_links WHERE hash = %s"
        params = [self.hash]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchall()

        if len(result) == 0:
            return self.scrap_product_link_deep()
        
        json_parsed = []
        for index, row in enumerate(result):
            if index >= config.max_quick_product_results:
                break
            tmp = {}
            tmp["hash"] = row[1]
            tmp["store"] = row[2]
            tmp["delivery"] = row[8]
            tmp["price"] = float(row[6]) if row[6] is not None else None
            tmp["returns"] = row[9]
            tmp["other_price"] = float(row[7]) if row[7] is not None else None
            tmp["link"] = row[3]
            tmp["scraped"] = row[4].strftime("%Y-%m-%d %H:%M:%S")
            tmp["last_scraped"] = row[5].strftime("%Y-%m-%d %H:%M:%S")
            tmp["new_hash"] = row[10] 
            json_parsed.append(tmp)
        
        con.close()
 
        return jsonify(json_parsed)

    def scrap_product_link_deep(self):
        con = self.con
        main_link = self.main_link

        logger.info(f"Deep search product links for {self.hash}")
        self.driver.get(main_link)
        self.page_source = WebDriverWait(self.driver, config.webload_timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, "UAVKwf")))

        rows = self.driver.find_elements(By.CLASS_NAME, "sh-osd__offer-row")
        tmp = [] 

        for index, row in enumerate(rows):
            if index >= config.max_deep_product_results:
                break

            store_element = row.find_element(By.CLASS_NAME, "b5ycib")
            store = store_element.text.encode("ascii", "ignore").decode("utf-8")

            try:
                delivery_element = row.find_element(By.CLASS_NAME, "yGibJf")
                delivery = delivery_element.text.encode("ascii", "ignore").decode("utf-8")
            except:
                delivery = None
                
            try:
                returns = delivery.split("\n")[1]
                delivery = delivery.split("\n")[0]
            except:
                returns = None


            price = None
            try:
                price_element = row.find_element(By.CLASS_NAME, "g9WBQb").text.encode("ascii", "ignore").decode("utf-8")
                price = price_element.replace("₹", "").replace(",", "").replace("$", "").replace("Rs."," ")
                price = re.findall(r'\d+\.\d+|\d+', price) 
                price = [float(value) for value in price][0]
            except:
                price = None

            other_price = None
            try:        
                other_price_element = row.find_element(By.CLASS_NAME, "hbp0ed").text.encode("ascii", "ignore").decode("utf-8")
                other_price = other_price_element.replace("₹", "").replace(",", "").replace("$", "").replace("Rs."," ")
                other_price = re.findall(r'\d+\.\d+|\d+', other_price)
                other_price = [float(value) for value in other_price][0]
            except:
                other_price = None
            
            link_element = row.find_element(By.CLASS_NAME, "shntl")
            link = link_element.get_attribute("href")

            timern = time.strftime('%Y-%m-%d %H:%M:%S')

            tmp.append({
                "hash": self.hash,
                "store": store,
                "delivery": delivery,
                "returns": returns,
                "price": price,
                "other_price": other_price,
                "link": link,
                "scraped": timern,
                "last_scraped": timern,
                "new_hash": hashlib.md5((store + self.hash).encode()).hexdigest()
            }) 

        val = []

        for product in tmp:
            for key, value in product.items():
                if value is None:
                    product[key] = None
                

            val.append((
                str(product["hash"]), str(product["store"]), str(product["delivery"]), product["price"], product["returns"],
                product["other_price"], str(product["link"]), product["scraped"], product["last_scraped"], str(product["new_hash"])
            )) 

            
        sql = """INSERT INTO product_links (
            hash,
            store,
            delivery,
            price,
            returns,
            other_price,
            link,
            scraped,
            last_scraped,
            new_hash
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE last_scraped=VALUES(last_scraped), price=VALUES(price), delivery=VALUES(delivery), returns=VALUES(returns), other_price=VALUES(other_price)
        """ 
        
        con.cursor.executemany(sql, val)
        con.db.commit() 

        logger.info(f"Successfully inserted {len(tmp)} product links into the database")

        self.scrap_reviews()
        
        con.close()

        return tmp
    
    def get_reviews(self):
        con = self.con

        sql = "SELECT * FROM product_reviews WHERE hash = %s"
        params = [self.hash]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchone()

        if result is None:
            return jsonify({"error": "Product hash not found in reviews or reviews not available for product, try deep search"}), 404

        """
        sql = (CREATE TABLE IF NOT EXISTS product_reviews (
 0   id INT AUTO_INCREMENT PRIMARY KEY,
 1  hash VARCHAR(32) UNIQUE,
 2   rating DECIMAL(3, 1),
 3   reviews_link LONGTEXT,
 4   reviews INT,
 5   one_star INT,
 6   two_star INT,
 7   three_star INT,
 8   four_star INT,
 9   five_star INT,
 10   tags LONGTEXT,
 11   scraped DATETIME,
 12   last_scraped DATETIME
)
"""
        rev_out = {}

        try:
            tags = result[10].replace("[", "").replace("]", "").replace("'", "").split(", ")
        except:
            tags = None

        try:
            stars = {
            "5": result[5],
            "4": result[6],
            "3": result[7],
            "2": result[8],
            "1": result[9]
        }
        except:
            stars = {
            "1": None,
            "2": None,
            "3": None,
            "4": None,
            "5": None
            }

        rev_out["hash"] = result[1]
        rev_out["rating"] = result[2]
        rev_out["reviews_link"] = result[3]
        rev_out["reviews"] = result[4]
        rev_out["tags"] = tags
        rev_out["stars"] = stars
        rev_out["scraped"] = result[11].strftime("%Y-%m-%d %H:%M:%S")
        rev_out["last_scraped"] = result[12].strftime("%Y-%m-%d %H:%M:%S")

        con.close()
        return jsonify(rev_out)


    def scrap_reviews(self):
        hash = self.hash

        logger.info(f"Deep search product reviews for {hash}")
        tags = []
        page_tags = self.driver.find_element(By.CLASS_NAME, "QPborb")
        tags_text = page_tags.find_elements(By.TAG_NAME, "a")
        
        try:
            for tag in tags_text:
                tags.append(tag.text.split("\n")[0])
        except:
            tags = None

        try:
            rating = self.driver.find_element(By.CLASS_NAME, "uYNZm").text
            rating = float(rating)
        except:
            rating = None

        try:
            reviews = self.driver.find_element(By.CLASS_NAME, "qIEPib").text.split(" ")[0].replace(",", "")
            reviews = int(reviews)
        except:
            reviews = None

        try:
            reviews_link = self.driver.find_element(By.CLASS_NAME, "Ba4zEd").get_attribute("href")
        except:
            reviews_link = None

        star_ratings = ["1", "2", "3", "4", "5"]
        review_counts = {'1': -1, '2': -1, '3': -1, '4': -1, '5': -1}

        try:
            elementss = self.driver.find_elements(By.CLASS_NAME, "wNgfq")
            for index, element in enumerate(elementss):
                review_counts[star_ratings[index]] = int(element.get_attribute("aria-label").split(" ")[0].replace(",", ""))
        except:
            review_counts = {'1': -1, '2': -1, '3': -1, '4': -1, '5': -1}

        con = self.con
        sql = """INSERT INTO product_reviews (
            hash,
            rating,
            reviews_link,
            reviews,
            one_star,
            two_star,
            three_star,
            four_star,
            five_star,
            tags,
            scraped,
            last_scraped
        ) VALUES (%s, %s, %s, %s, %s,%s, %s,%s, %s,%s, %s,%s)
        ON DUPLICATE KEY UPDATE last_scraped=VALUES(last_scraped), rating=VALUES(rating), reviews=VALUES(reviews), one_star=VALUES(one_star), two_star=VALUES(two_star), three_star=VALUES(three_star), four_star=VALUES(four_star), five_star=VALUES(five_star), tags=VALUES(tags)
        """

        timern = time.strftime('%Y-%m-%d %H:%M:%S')

        val = (
            hash, rating, reviews_link, reviews, review_counts["1"], review_counts["2"], review_counts["3"], review_counts["4"], review_counts["5"], str(tags), timern, timern
        )

        con.cursor.execute(sql, val)
        con.db.commit()

        logger.info(f"Successfully inserted product reviews into the database")


    def scrap_product_data_db(self, go4deep=False):
        con = self.con
        keywords = self.rproduct.split(" ")
        
        # sql = "SELECT * FROM products WHERE " + " OR ".join(["tags LIKE %s"] * len(keywords)) + " OR hash = %s"

        sql = "SELECT * FROM products WHERE " + " OR ".join(["tags LIKE %s"] * len(keywords)) + " OR hash = %s"
        params = ["%" + keyword + "%" for keyword in keywords] + [self.hash]
        con.cursor.execute(sql, params)
        result = con.cursor.fetchall()

        if len(result) == 0:
            if go4deep:
                self.scrape_product_data()
                return self.product_data
            else:
                return jsonify({"error": "Product not found, try deep search"}), 404
            
        json_parsed = []

        for index, row in enumerate(result):
            if index > config.max_quick_search_results:
                break
            tmp = json_format_1.copy()
            tmp["additional_info"] = row[14]
            tmp["hash"] = row[2]
            tmp["img"] = row[3]
            tmp["in_stock"] = row[11]
            tmp["last_scraped"] = row[18]
            tmp["link"] = row[10]
            tmp["market"] = row[4]
            tmp["other_links"] = row[16].split(" ")
            tmp["other_price"] = row[7]
            tmp["price"] = row[6]
            tmp["price_description"] = row[15]
            tmp["rating"] = {
                "reviews": row[8],
                "score": row[9]
            }
            tmp["scraped"] = row[17]
            tmp["shipping"] = row[5]
            if row[1] is not None:
                tmp["tags"] = [tag for tag in row[1].split(" ") if tag.isalnum()]
                tmp["title"] = row[1]
            else:
                tmp["tags"] = None
                tmp["title"] = row[2]
            tmp["verified"] = row[12]
            json_parsed.append(tmp)

        con.close()
        return json_parsed

    def scrape_product_data(self):
        logger.info(f"Deep search product data for {self.product}")
        self.driver.get(self.url) # headers=config.headers
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

                if class_name == "EI11Pd" or class_name == "EI11Pd Hb793d":
                    if not text or text == " " or text == "" or text == None:
                        text = self.rproduct
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

        con = self.con

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
        con.close()
        return self.product_data
