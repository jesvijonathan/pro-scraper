from flask import Blueprint, request, jsonify
from flask.views import MethodView
from logger import logger
import scrapy

search_bp = Blueprint('search', __name__)

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

        if self.path == '/search':
            return result.scrap_product_data_db()
        elif self.path == '/search/deep_search':
            return result.scrape_product_data()
        elif self.path == '/search/quick_search':
            return result.scrap_product_data_db()
        else:
            return jsonify({'error': 'Invalid URL'}), 404

    def get(self):
        logger.info(f"GET \"{self.path}\" {self.ip} {str(self.form)} {str(self.request.args)}")
        return self.handle_search(lambda result: result.scrape_product_data())

    def post(self):
        logger.info(f"POST \"{self.path}\" {self.ip} {str(self.form)}")
        if self.path == '/search/productPage':
            return jsonify({'message': 'This is a /search/productPage POST request'})
        return self.handle_search(lambda result: result.scrape_product_data())

search_bp.add_url_rule('/search', view_func=SearchView.as_view('search_product_view'))
search_bp.add_url_rule('/search/productPage', view_func=SearchView.as_view('search_productPage_view'))
search_bp.add_url_rule('/search/quick_search', view_func=SearchView.as_view('search_quickSearch_view'))
search_bp.add_url_rule('/search/deep_search', view_func=SearchView.as_view('search_deepSearch_view'))
