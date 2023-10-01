logger_append = False   # set to True to append logs.log | False to overwrite
logger_console_print = False   # set to True to print logs to console
logger_tail = True   # set to True to tail live logs.log

env_os = 1       # 0 : "linux" or 1 : "windows"

# set to path of chromedriver.exe | leave blank to use default/auto
chromedriver_path = ""
chromedriver_mode = 0       # 0 : "headless" or 1 : "normal" or 2 : "maximized"
# set to number of chromedriver instances to run in parallel
chromedriver_pool_size = 4
# set to number of seconds to wait for a chromedriver instance to become available
chromedriver_timeout = 10

debug_mode = True    # set to True to enable debug mode
use_reloader = True   # set to True to enable auto reload on code changes
app_port = 5000    # set to port number to run server on
threaded = True    # set to True to enable multi-threading

max_quick_search_results = 99      # set to max number of quick search results to return
max_search_results = 10      # set to max number of search results to return (deep search results, higher value scraps more data)
max_quick_product_results = 99      # set to max number of quick product links results to return after search from db
max_deep_product_results = 10      # set to max number of deep product links results to return after search from db (higher value scraps more data)
webload_timeout = 30      # set to number of seconds to wait for a webpage to load

database_host = "localhost"
database_user = "root"
database_password = ""
database_name = "pro_scraper"


secret_key = "secret key"