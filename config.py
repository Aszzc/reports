import pymongo
import ntplib
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

#scrapy config
SPIDER_NAME = 'dfcf_spider'
MONGODB_URI = "mongodb://localhost:27017/"  # MongoDB服务器地址
MONGODB_DB = "ReportsLibs"  # 数据库名称
MONGODB_COLLECTION = "dfcf"  # 集合名称
MONGODB_INDEX = "encodeUrl"

ENABLE_PIPELINE = True

#time config
NTP_SERVER = 'pool.ntp.org'
def now():
    client = ntplib.NTPClient()
    try:
        response = client.request(NTP_SERVER)
        ntp_time_utc = datetime.utcfromtimestamp(response.tx_time)
        ntp_time_plus_eight = ntp_time_utc + timedelta(hours=8)
        return ntp_time_plus_eight.strftime('%Y-%m-%d')
    except ntplib.NTPException as e:
        return False

#url config
#copy form f12-network
APIs = {
    'hyyj': 'https://reportapi.eastmoney.com/report/list?cb=datatable5598584&industryCode=*&pageSize=50&industry=*&rating=*&ratingChange=*&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=1&orgCode=&rcode=&p=2&pageNum=2&pageNumber=2&_=1702429848211',
    'ggyj': 'https://reportapi.eastmoney.com/report/list?cb=datatable4813486&industryCode=*&pageSize=50&industry=*&rating=&ratingChange=&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=0&orgCode=&code=*&rcode=&p=2&pageNum=2&pageNumber=2&_=1702429815344',
    'hgyj': 'https://reportapi.eastmoney.com/report/jg?cb=datatable624430&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=3&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429925208',
    'clyb': 'https://reportapi.eastmoney.com/report/jg?cb=datatable5964799&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=2&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429948047',
    'qscb': 'https://reportapi.eastmoney.com/report/jg?cb=datatable3770536&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=4&orgCode=&author=&p=2&pageNum=2&pageNumber=2&_=1702429970232',
    # 'xgyj': 'https://reportapi.eastmoney.com/report/newStockList?cb=datatable3619528&pageSize=50&beginTime=2021-12-13&endTime=2023-12-13&pageNo=2&fields=&qType=4&p=2&pageNum=2&pageNumber=2&_=1702429987997'
}

def geturl(task, btime, etime, page, page_size=100):
    url = APIs[task]
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    query_params['pageNo'] = [str(page)]
    query_params['beginTime'] = [str(btime)]
    query_params['endTime'] = [str(etime)]
    query_params['cb'] = []
    query_params['pageSize'] = [str(page_size)]

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


#db config
def init_mongo():
    client = pymongo.MongoClient(MONGODB_URI)
    db = client[MONGODB_DB]
    collection = db[MONGODB_COLLECTION]
    return collection
#get lasted db records date

def lasted():
    db = init_mongo()

    lasted_data = db.find().sort({'publishDate':-1}).limit(1)[0]['publishDate']
    first_data = db.find().sort({'publishDate':1}).limit(1)[0]['publishDate']
    lasted_data = datetime.strptime(lasted_data, '%Y-%m-%d %H:%M:%S.%f').date()
    first_data = datetime.strptime(first_data, '%Y-%m-%d %H:%M:%S.%f').date()

    return lasted_data
