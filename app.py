
import chromedriver
from search_controller import search_bp
import scrapy
import atexit
import threading
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
import re
import MySQLdb.cursors
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
import config
from logger import logger
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


app.register_blueprint(search_bp)
logger.info("Registered Blueprints")


chromedriver.init_chromedriver_pool()


@app.route('/', methods=['GET'])
def index():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    path = request.path
    logger.info("GET \"" + path + "\" " + str(ip))

    return render_template('index.html')


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
    logger.error("\""+path + "\" 404 " + str(ip))

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
    use_reloader = config.use_reloader
    threaded = config.threaded
    app.run(debug=debug_mode, port=app_port,
            use_reloader=use_reloader, threaded=threaded)
