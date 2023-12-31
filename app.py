from flask import Flask, request, render_template, jsonify
import sys
sys.path.append('.')

import config as cfg
import os
import requests
import subprocess
from flask_caching import Cache

os.environ['TODAY_DATE'] = cfg.now()
os.environ['INIT_DATE'] = '2020-01-01'

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

#实时响应程序
# @app.route('/api/realtime')
@app.route('/')
def realtime():
    return render_template('realtime.html')

@app.route('/api/realtime/get_data_by_task')
@cache.cached(timeout=600)  # 设置缓存过期时间为60秒
def get_data_by_task():
    task = request.args.get('task',default='hhyj')
    page = request.args.get('page', default=1)

    etime = os.environ.get('TODAY_DATE')
    btime = os.environ.get('INIT_DATE')

    data = []

    if task in cfg.APIs.keys():
        new_url = cfg.geturl(task=task, btime=btime, etime=etime, page=page)
        try:
            r = requests.get(new_url)
            r.raise_for_status()  # Raise an HTTPError for bad responses
            r_data = r.json()['data']
            data.extend(r_data)
        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., connection error)
            return jsonify({'error': f'Request failed: {str(e)}'}), 500
    else:
        for key, value in cfg.APIs.items():
            new_url = cfg.geturl(task=key, btime=btime, etime=etime, page=page)
            try:
                r = requests.get(new_url)
                r.raise_for_status()
                r_data = r.json()['data']
                data.extend(r_data)
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Request failed for {key}: {str(e)}'}), 500

    return jsonify(data)


#数据检索程序
@app.route('/api/search')
def search():
    global mongo
    mongo = cfg.init_mongo()
    return render_template('search.html')


@app.route('/api/search/search_data_by_keywords')
def search_data_by_keywords():
    q = request.args.get('q')
    regex_pattern = f".*{q}.*"
    query = {
        "$or": [
            {"title": {"$regex": regex_pattern, "$options": "i"}},
            {"stockName": {"$regex": regex_pattern, "$options": "i"}},
            {"stockCode": {"$regex": regex_pattern, "$options": "i"}},
            {"industryName": {"$regex": regex_pattern, "$options": "i"}},
            {"publishDate": {"$regex": regex_pattern, "$options": "i"}},
        ]
    }
    projection = {
        '_id': 0,
        'title': 1,
        'infoCode': 1,
        'encodeUrl': 1,
        'attachPages': 1,
        'publishDate': 1,
        'industryName': 1,
        'stockName': 1,
    }
    sort_field = 'attachPages'
    sort_order = -1
    results = list(mongo.find(query, projection).sort(sort_field, sort_order).limit(500))
    return results


#更新数据
#http://127.0.0.1:5000/api/update
@app.route('/api/update')
def update():
    today_date = cfg.now()
    init_date = cfg.lasted()

    os.chdir('./spider_main')
    subprocess.run(['scrapy', 'crawl', f'{cfg.SPIDER_NAME}', '-a', f'today_date={today_date}', '-a',  f'init_date={init_date}'])
    return 'Scrapy spider is running.'

if __name__ == '__main__':
    app.run(debug=True, threaded = True)
