
import chromedriver
from search_controller import search_bp
import atexit
from selenium import webdriver
from flask import Flask, render_template, request, redirect, url_for, flash, session
import config
from logger import logger

import mysql.connector
import time

logger.info("\n ############################### \n")
logger.info("Starting program")
logger.info("Logger initialized")
logger.info("Loading Configuration")
logger.info("Logger append        : " + str(config.logger_append))
logger.info("Logger console print : " + str(config.logger_console_print))
logger.info("Logger tail          : " + str(config.logger_tail))
logger.info("Environment OS       : " + str(config.env_os))
logger.info("ChromeDriver path    : \"" + str(config.chromedriver_path) + "\"")
logger.info("ChromeDriver mode    : " + str(config.chromedriver_mode))
logger.info("ChromeDriver pool    : " + str(config.chromedriver_pool_size))
logger.info("ChromeDriver timeout : " + str(config.chromedriver_timeout))
logger.info("Debug mode           : " + str(config.debug_mode))
logger.info("Use reloader         : " + str(config.use_reloader))
logger.info("App port             : " + str(config.app_port))
logger.info("Threaded             : " + str(config.threaded))


# from flask_mysqldb import MySQL
# from flask_mail import Mail, Message
logger.info("Imported all modules")

logger.info("Imported In-House modules")




app = Flask(__name__)




db = mysql.connector.connect(
host=config.database_host,
user=config.database_user,
password=config.database_password)

cursor = db.cursor(buffered=True)
sql = "CREATE DATABASE IF NOT EXISTS {s0}".format(s0=config.database_name)
cursor.execute(sql)

cursor.close()
db.close()
logger.info("MySQL database created")

db = mysql.connector.connect(
host=config.database_host,
user=config.database_user,
password=config.database_password,
database=config.database_name )
cursor = db.cursor(buffered=True)

logger.info("MySQL cursor created")




"""
{
  "title": "Apple iPhone 13 (128GB, Midnight)",
  "tags": ["Apple", "iPhone", "13", "128GB,", "Midnight"],
  "market": "Reliance Digital",
  "price": "54900.00",
  "rating": {
    "reviews": "8,723",
    "score": "4.6"
  },
  "in_stock": "",
  "shipping": "Free delivery by 3 Oct and free 5-day returns",
  "verified": false,
  "price_description": "",
  "additional_info": "Smartphone  Dual SIM  5G",
  "img": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcSdbMcu_sYPXLZcOuSnCAAleUSFoclkU1qgAQmPdw_fDIGB7gFF4bHInfXkp9pt6e5l3lxuK2RVAQjVI2G3ji5KRMBR1XMJLfCUjeuQDB__&usqp=CAE",
  "links": [
    "https://www.google.com/url?url=https://www.reliancedigital.in/apple-iphone-13-128-gb-midnight-black-/p/491997699%3Fsrsltid%3DAfmBOopVnn4-1tzEQMo89wA9KWyO_OtVL7yHKBRSacTmY-TW_Esr82pJJ0I&rct=j&q=&esrc=s&opi=95576897&sa=U&ved=0ahUKEwiHnsSA68iBAxUcSmwGHUXJAxwQguUECMcM&usg=AOvVaw0NI9j7lMJZ6KwAeDoH_8N_",
    "https://www.google.com/shopping/product/10864203085039380343?q=iphone+13&prds=eto:10603666471394521545_0,pid:7634124128593707086,rsk:PC_4079606304177687932&sa=X&ved=0ahUKEwiHnsSA68iBAxUcSmwGHUXJAxwQ8gIIvwwoAA",
    "https://www.google.com/shopping/product/10864203085039380343/offers?q=iphone+13&prds=eto:10603666471394521545_0,pid:7634124128593707086,rsk:PC_4079606304177687932&sa=X&ved=0ahUKEwiHnsSA68iBAxUcSmwGHUXJAxwQ3q4ECMoM"
  ],
  "scraped": 1695750538.90776
}"""


sql = ("""CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    hash VARCHAR(32) UNIQUE,
    img VARCHAR(255),
    market VARCHAR(255),
    shipping VARCHAR(255),
    price DECIMAL(10, 2),
    other_price DECIMAL(10, 2),
    reviews INT,
    score DECIMAL(3, 1),
    link LONGTEXT,
    in_stock VARCHAR(255),
    verified BOOLEAN,      
    tags VARCHAR(255),
    additional_info VARCHAR(255),
    price_description VARCHAR(255),
    other_links LONGTEXT,
    scraped DATETIME,
    last_scraped DATETIME
)""")

cursor.execute(sql)


sql = ("""CREATE TABLE IF NOT EXISTS product_links (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hash VARCHAR(32),
    store VARCHAR(255),
    link LONGTEXT,
    scraped DATETIME,
    last_scraped DATETIME,
    price DECIMAL(10, 2),
    other_price DECIMAL(10, 2),
    delivery VARCHAR(255),
    returns VARCHAR(255),
    new_hash VARCHAR(32) UNIQUE
       
)""")

cursor.execute(sql)


sql = ("""CREATE TABLE IF NOT EXISTS product_reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hash VARCHAR(32) UNIQUE,
    rating DECIMAL(3, 1),
    reviews_link LONGTEXT,
    reviews INT,
    one_star INT,
    two_star INT,
    three_star INT,
    four_star INT,
    five_star INT,
    tags LONGTEXT,
    scraped DATETIME,
    last_scraped DATETIME
)""")

cursor.execute(sql)

cursor.close()
db.close()
logger.info("MySQL tables created")



app.secret_key = config.secret_key
logger.info("Secret key set")



app.register_blueprint(search_bp)
logger.info("Registered Blueprints")


chromedriver.init_chromedriver_pool()


@app.route('/', methods=['GET'])
def index2():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    return render_template('main.html')

@app.route('/deep', methods=['GET'])
def index():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))

    return render_template('index.html')

@app.route('/quick', methods=['GET'])
def index_db_search():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    return render_template('searchdb.html')

@app.route('/product', methods=['GET'])
def index_product():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    return render_template('product.html')

@app.route('/reviews', methods=['GET'])
def index_reviews():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    return render_template('rev.html')

@app.route('/restart', methods=['GET'])
def restart():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    chromedriver.restart_all_chrome_drivers()
    return "Restarted all ChromeDriver instances"

@app.route('/restart_db', methods=['GET'])
def restart_db():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))
    # restart connection to database
    db = mysql.connector.connect(
    host=config.database_host,
    user=config.database_user,
    password=config.database_password,
    database=config.database_name )
    cursor = db.cursor(buffered=True)
    logger.info("MySQL cursor created")
    # close connection to database
    time.sleep(1)
    cursor.close()
    db.close()
    logger.info("MySQL connection closed")

    return "Restarted a connection"

"""
    driver = chromedriver.get_chromedriver()
    if driver:
        try:
            driver.get("https://www.google.com")
            return driver.page_source
        finally:
            chromedriver.release_chromedriver(driver)
    else: 
        logger.error("Failed to get chromedriver instance")
"""

    
@app.route('/searchProduct', methods=['POST'])
def searchProduct():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    form_data = request.form.to_dict()
    logger.info("POST \"" + path + "\" " + str(ip) + " " + str(form_data))

    return "true"


@app.route("/productPage", methods=['GET'])
def productPage():
    return "True"


@app.errorhandler(404)
def page_not_found(e):
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.error("\""+path + "\" 404 " + str(ip) + " " + str(e))

    return render_template('404.html'), 404


def cleanup():
    logger.info("Cleaning up")

    chromedriver.chrome_driver_queue.join()
    chromedriver.close_chromedriver_pool()
    logger.info("ChromeDriver pool closed")

    logger.info("Exiting program")


atexit.register(cleanup)

if __name__ == "__main__":
    debug_mode = config.debug_mode or False
    app_port = config.app_port or 5000
    use_reloader =   config.use_reloader
    threaded = config.threaded
    app.run(debug=debug_mode, port=app_port) 
    #use_reloader=use_reloader, threaded=threaded)


# Pro Scraper | By Jesvi Jonathan


# /                     | Home | Deep Search Console
# /quick                | Quick Search Console
# /restart              | Restart all ChromeDriver instances
# /product              | Product Console
# /reviews              | Reviews Console

# /api/search           | Deep Search API
# /api/quick_search     | Quick Search API
# /api/deep_search      | Deep Search API

# /api/product          | Product API
# /api/product_quick    | Product API
# /api/product_deep     | Product API

# you can pass searchQuery as a GET parameter or as a POST parameter via form data or JSON data

# use searchQuery with search API
# exmaple : /api/search?searchQuery=iphone+13

# use product Hash with product API | you can get product hash from search resopnse
# exmaple : /api/product_quick?searchQuery=01e54b2ceb0307cfa650615282ec8239