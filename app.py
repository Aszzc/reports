from flask import Flask, request, render_template, jsonify
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
import ntplib
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

ntp_server = 'pool.ntp.org'

def init_app():
    global api_urls
    api_urls = {
        'api_hyyj': 'https://reportapi.eastmoney.com/report/list?cb=datatable5598584&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=1&orgCode=&rcode=&p=2&pageNum=2&pageNumber=2&_=1702429848211',
        'api_ggyj': 'https://reportapi.eastmoney.com/report/list?cb=datatable4813486&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=0&orgCode=&code=*&rcode=&p=2&pageNum=2&pageNumber=2&_=1702429815344',
        'api_hgyj': 'https://reportapi.eastmoney.com/report/jg?cb=datatable624430&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=3&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429925208',
        'api_clyb': 'https://reportapi.eastmoney.com/report/jg?cb=datatable5964799&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=2&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429948047',
        'api_qscb': 'https://reportapi.eastmoney.com/report/jg?cb=datatable3770536&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=4&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429970232',
        # 'api_xgyj': 'https://reportapi.eastmoney.com/report/newStockList?cb=datatable3619528&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=4&p=2&pageNum=2&pageNumber=2&_=1702429987997'
    }

init_app()

def update_url_page(url, btime, etime, npage):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params['pageNo'] = [str(npage)]
    query_params['beginTime'] = [str(btime)]
    query_params['endTime'] = [str(etime)]
    query_params['cb'] = []
    updated_query = urlencode(query_params, doseq=True)

    updated_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        updated_query,
        parsed_url.fragment
    ))

    return updated_url

def get_date():
    client = ntplib.NTPClient()
    try:
        response = client.request(ntp_server)
        ntp_time_utc = datetime.utcfromtimestamp(response.tx_time)
        ntp_time_plus_eight = ntp_time_utc + timedelta(hours=8)
        return ntp_time_plus_eight.strftime('%Y-%m-%d')
    except ntplib.NTPException as e:
        return f'Error connecting to NTP server: {e}'


@app.route('/api/data_by_task')
def data_by_task():
    task = request.args.get('task',default='api_hhyj')
    page = request.args.get('page', default=1)

    today_date = get_date()
    etime = today_date
    btime = '2020-01-01'

    data = []

    if task in api_urls:
        url = api_urls[task]
        new_url = update_url_page(url=url, btime=btime, etime=etime, npage=page)
        try:
            r = requests.get(new_url)
            r.raise_for_status()  # Raise an HTTPError for bad responses
            r_data = r.json()['data']
            data.extend(r_data)
        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., connection error)
            return jsonify({'error': f'Request failed: {str(e)}'}), 500
    else:
        for key, value in api_urls.items():
            new_url = update_url_page(url=value, btime=btime, etime=etime, npage=page)
            try:
                r = requests.get(new_url)
                r.raise_for_status()
                r_data = r.json()['data']
                data.extend(r_data)
            except requests.exceptions.RequestException as e:
                return jsonify({'error': f'Request failed for {key}: {str(e)}'}), 500

    return jsonify(data)



@app.route('/')
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
