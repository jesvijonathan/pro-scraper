from flask import Blueprint, request, jsonify
from flask.views import MethodView
from logger import logger
import scrapy

search_bp = Blueprint('api', __name__)

class SearchView(MethodView):
    def __init__(self):
        self.request = request
        self.form = request.form.to_dict()
        self.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        self.path = request.path

    def handle_search(self, search_method):
        search_query = self.form.get('searchQuery') or request.args.get('searchQuery') 

        if not search_query:
            return jsonify({'error': 'Missing searchQuery parameter'}), 400

        result = scrapy.GoogleScrapy(search_query)

        try:
            if self.path == '/api/search':
                return result.scrap_product_data_db(go4deep=True)
            elif self.path == '/api/deep_search':
                return result.scrape_product_data()
            elif self.path == '/api/db_search':
                return result.scrap_product_data_db()
            elif self.path == '/api/quick_search':
                return result.scrap_product_data_db()
            elif self.path == '/api/product':
                return result.scrap_product()
            elif self.path == '/api/product_quick':
                return result.scrap_product()
            elif self.path == '/api/product_deep':
                return result.scrap_product(deep=True)
            elif self.path == '/api/reviews':
                return result.get_reviews()
            elif self.path == '/api/refresh_product':
                return result.ref_product()
            else:
                return jsonify({'error': 'Invalid URL'}), 404
        except Exception as e:
            logger.error(f"Exception: {str(e)}")
            return jsonify({'error': str(e)}), 500

    def get(self):
        logger.info(f"GET \"{self.path}\" {self.ip} {str(self.form)} {str(self.request.args)}")
        return self.handle_search(lambda result: result.scrape_product_data())

    def post(self):
        logger.info(f"POST \"{self.path}\" {self.ip} {str(self.form)}")
        return self.handle_search(lambda result: result.scrape_product_data())

search_bp.add_url_rule('/api/search', view_func=SearchView.as_view('search_search_view'))
search_bp.add_url_rule('/api/quick_search', view_func=SearchView.as_view('search_quickSearch_view'))
search_bp.add_url_rule('/api/deep_search', view_func=SearchView.as_view('search_deepSearch_view'))
search_bp.add_url_rule('/api/product', view_func=SearchView.as_view('search_product_view'))  # Use a unique endpoint name here
search_bp.add_url_rule('/api/product_quick', view_func=SearchView.as_view('search_productQuick_view'))  # Use a unique endpoint name here
search_bp.add_url_rule('/api/product_deep', view_func=SearchView.as_view('search_productDeep_view'))  # Use a unique endpoint name here
search_bp.add_url_rule('/api/reviews', view_func=SearchView.as_view('search_reviews_view'))  # Use a unique endpoint name here
search_bp.add_url_rule('/api/db_search', view_func=SearchView.as_view('search_dbSearch_view'))  # Use a unique endpoint name here
search_bp.add_url_rule('/api/refresh_product', view_func=SearchView.as_view('search_refreshProduct_view'))  # Use a unique endpoint name here