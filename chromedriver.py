import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import queue
import time
from logger import logger

NUM_CHROMEDRIVERS = config.chromedriver_pool_size


def init_chromedriver():
    chrome_options = get_driver_mode()
    return get_webdriver(chrome_options)

def get_driver_mode():
    options = webdriver.ChromeOptions()

    if config.chromedriver_mode == 0:
        options.add_argument("--headless")
    elif config.chromedriver_mode == 2:
        options.add_argument("--start-maximized")
    logger.info("Using chromedriver mode: " + str(config.chromedriver_mode))
     
    return options

def get_webdriver(chrome_options):
    if config.chromedriver_path:
        logger.info("Using User defined chromedriver path")
        return webdriver.Chrome(executable_path=config.chromedriver_path, options=chrome_options)
    else:
        if config.env_os == 0:
            logger.info("Using default linux chromedriver")
            return webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_options)
        elif config.env_os == 1:
            
            logger.info("Using default windows chromedriver")
            return webdriver.Chrome(executable_path="C:\chromedriver.exe", options=chrome_options)
        else:
            logger.error("Invalid OS/Path")
            return None

chrome_driver_queue = queue.Queue()

def init_chromedriver_pool():
    global chrome_driver_queue
    logger.info("Initializing ChromeDriver pool...")
    for _ in range(NUM_CHROMEDRIVERS):
        driver = init_chromedriver()
        if driver:
            chrome_driver_queue.put(driver)
    logger.info("Initialized ChromeDriver pool with " + str(NUM_CHROMEDRIVERS) + " instances")

def get_chromedriver(timeout=config.chromedriver_timeout):
    start_time = time.time()
    while True:
        try:
            driver = chrome_driver_queue.get(timeout=timeout)
            logger.info("Getting ChromeDriver instance")
            return driver
        except queue.Empty:
            if time.time() - start_time > timeout:
                logger.warning("Timeout: No available ChromeDriver instances in the pool")
                return None
            else:
                time.sleep(1)

def release_chromedriver(driver):
    global chrome_driver_queue
    logger.info("Releasing ChromeDriver instance")
    chrome_driver_queue.put(driver)

def close_chromedriver_pool():
    global chrome_driver_queue
    while not chrome_driver_queue.empty():
        driver = chrome_driver_queue.get()
        try:
            driver.quit()   
        except Exception as e:
            print(f"Error while closing ChromeDriver instance: {str(e)}")
            

