logger_append = False   # set to True to append logs.log | False to overwrite
logger_console_print = False   # set to True to print logs to console
logger_tail = False   # set to True to tail live logs.log

env_os = 1       # 0 : "linux" or 1 : "windows"

# set to path of chromedriver.exe | leave blank to use default/auto
chromedriver_path = ""
chromedriver_mode = 0       # 0 : "headless" or 1 : "normal" or 2 : "maximized"
# set to number of chromedriver instances to run in parallel
chromedriver_pool_size = 2
# set to number of seconds to wait for a chromedriver instance to become available
chromedriver_timeout = 10

debug_mode = True    # set to True to enable debug mode
use_reloader = True   # set to True to enable auto reload on code changes
app_port = 5000    # set to port number to run server on
threaded = True    # set to True to enable multi-threading

max_search_results = 10      # set to max number of search results to return
webload_timeout = 30      # set to number of seconds to wait for a webpage to load