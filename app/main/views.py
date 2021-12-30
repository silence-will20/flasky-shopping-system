from flask import render_template, url_for, request
from app import user
from app.models import Basket, Commodity, Commodity_category, Store, User
from flask_login import current_user
import os, re
from PIL import Image

from . import main
@main.route('/')
def index(): 
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    dirpath = os.path.join('./app/static/recommending_commodity_images/', '')
    del_list = os.listdir(dirpath)
    for f in del_list:
        file_path = os.path.join(dirpath, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
    for i in range(recommending_commodities.count()):
        pathfrom = os.path.join('./app/static/commodity_images/', recommending_commodities[i].commodityimage)
        pathto = os.path.join('./app/static/recommending_commodity_images/', recommending_commodities[i].commodityimage)
        img = Image.open(pathfrom)
        out = img.resize((1140, 350),Image.ANTIALIAS)
        out.save(pathto, type='jpg')
    commodities = Commodity.query.all()
    return render_template('index.html', recommending_commodities=recommending_commodities, commodities=commodities)

@main.route('/category-commodities/<categoryid>')
def show_category_commodities(categoryid): 
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    commodities = Commodity.query.filter_by(commodity_category_id=categoryid).all()
    return render_template('show_category_commodities.html', categoryid=categoryid, commodities=commodities, recommending_commodities=recommending_commodities)

@main.route('/search-commodity-results', methods=['GET', 'POST'])
def search_commodity_results(): 
    user_input = request.form['search_input']
    suggestions = []
    pattern = '.*?'.join(user_input)    # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)         # Compiles a regex.
    commodities = Commodity.query.all()
    for com in commodities:
        match = regex.search(com.commodityname)      # Checks if the current item matches the regex.
        if match:
            suggestions.append(com)
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    return render_template('search_commodity_results.html', recommending_commodities=recommending_commodities, commodities=suggestions, user_input=user_input)

@main.route('/category-search-commodity-results/search=<user_input>/<categoryid>')
def category_search_commodity_results(categoryid, user_input): 
    suggestions = []
    pattern = '.*?'.join(user_input)    # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)         # Compiles a regex.
    commodities = Commodity.query.filter_by(commodity_category_id=categoryid).all()
    for com in commodities:
        match = regex.search(com.commodityname)      # Checks if the current item matches the regex.
        if match:
            suggestions.append(com)
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    return render_template('category_search_commodity_results.html', categoryid=categoryid, commodities=suggestions, recommending_commodities=recommending_commodities, user_input=user_input)

@main.route('/commodity-detail/<commodityid>')
def commodity_detail(commodityid): 
    recommending_commodities = Commodity.query.order_by(Commodity.sales_volume).limit(6)
    commodity = Commodity.query.get(commodityid)
    store_commodities = Commodity.query.filter_by(store_id=commodity.store_id).all()
    s = Store.query.get(commodity.store_id)
    storekeeper = User.query.get(s.user_id)
    if current_user.is_authenticated: 
        basket = Basket.query.filter_by(user_id=current_user.id, commodity_id=commodityid).first()
        return render_template('commodity_detail.html', store_commodities=store_commodities, commodity=commodity, recommending_commodities=recommending_commodities, storekeeper=storekeeper, basket=basket, s=s)
    else: 
        return render_template('commodity_detail.html', store_commodities=store_commodities, commodity=commodity, recommending_commodities=recommending_commodities, storekeeper=storekeeper, s=s)