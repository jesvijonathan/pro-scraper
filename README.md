# [Pro-Scraper](https://pro-scraper.vercel.app/)

- Clone repository to local machine
- install python, pip & mysql
- install python requirements.txt
- install mysql server ("winget install -e Oracle.MySQL" in terminal | or manual install from mysql website)
- setup mysql server, create user (make sure to grant all privileges | or use root user instead)
- sometimes you are required to set current use db (Set current database: "`use <database_name>;`")
- add user & mysql credentials to config.py
- start mysql server
- run python3 app.py
- open browser and go to http://localhost:5000
- Try scraping something. The more you scrape the more optimized it gets over time.
- you dont have to export data as csv, you can use the API to get data in JSON format or even better use the Database directly to fetch data.locally.
- fiddle around and have fun !

<!--
/ | Home | Search Console
/quick | Quick Search Console
/deep | Deep Search Console

/restart | Restart all ChromeDriver instances
/restart_db  | Restart your mysqld connection

/product | Product Console
/reviews | Reviews Console

/api/search | Search API
/api/quick_search | Quick Search API
/api/deep_search | Deep Search API

/api/product | Product API
/api/product_quick | Product API
/api/product_deep | Product API

you can pass searchQuery as a GET parameter or as a POST rameter via form data or JSON data
use searchQuery with search API
exmaple : /api/search?searchQuery=iphone+13

use product Hash with product API | you can get product hash from search resopnse
exmaple : /api/product_quick?searchQuery=01e54b2ceb0307cfa650615282ec8239 -->

<!-- url endpoints -->
<!-- create markdown -->

### Search API

- **URL**

  `/api/search`
  `/api/quick_search`
  `/api/deep_search`

  <br>

- **Method:**
- `GET`
- `POST`
  <br>
- **URL Params**
  <br>
  - **Required:**
    `searchQuery=[string]`
    <br>
- **Data Params**
- `searchQuery=[string]`
  <br>
- **Success Response:**

  - **Code:** 200
    **Content:** `{ searchQuery : "iphone 13" }`
    <br>

- **Error Response:**
- **Code:** 404 NOT FOUND
  **Content:** `{ error : "No results found" }`
  <br>
- **Sample Call:**

  ```javascript
  $.ajax({
    url: "http://localhost:5000/api/search?searchQuery=iphone+13",
    dataType: "json",
    type: "GET",
    success: function (r) {
      console.log(r);
    },
  });
  ```

  ```javascript
  $.ajax({
    url: "http://localhost:5000/api/search",
    dataType: "json",
    type: "POST",
    data: { searchQuery: "iphone 13" },
    success: function (r) {
      console.log(r);
    },
  });
  ```

  <!-- other url -->

<br>
## Other Endpoints :

- `api/search/product`
- `api/search/product_quick`
- `api/search/product_deep`
  <br>
- `api/search/reviews`
- `api/search/reviews_quick`
- `api/search/reviews_deep`
  <br>
- `api/search/search`
- `api/search/search_quick`
- `api/search/search_deep`
