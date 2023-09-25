from flask import Blueprint, request, jsonify, redirect, url_for, render_template
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

    def get(self):
        logger.info("GET \"" + self.path + "\" " + str(self.ip))
        return jsonify({'message': 'GET method not allowed'})

    def post(self):
        logger.info("POST \"" + self.path + "\" " + str(self.ip) + " " + str(self.form))
        if self.path == '/search':
            return self.postSearch()
        elif self.path == '/search/productPage':
            return self.postProductPage()
        else:
            return jsonify({'error': 'Invalid URL'}), 404
    
    def postSearch(self):
        result = scrapy.GoogleScrapy(self.form['searchQuery'])
        act_res = result.scrape_product_data()
        return act_res
    
    def postProductPage(self):
        return jsonify({'message': 'This is a /search/productPage POST request'})
    
search_bp.add_url_rule('/search', view_func=SearchView.as_view('search_product_view'))
search_bp.add_url_rule('/search/productPage', view_func=SearchView.as_view('search_productPage_view'))
