# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection, index):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.index = index
        

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        mongo_uri = settings.get('MONGODB_URI')
        mongo_db = settings.get('MONGODB_DB')
        mongo_collection = settings.get('MONGODB_COLLECTION')
        index = settings.get('MONGODB_INDEX')
        return cls(mongo_uri, mongo_db, mongo_collection, index)

    def open_spider(self, spider):
        # 在Spider启动时连接MongoDB并设置索引
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.collection = self.db[self.mongo_collection]
        self.collection.create_index([(self.index,pymongo.ASCENDING)], unique=True)

    def process_item(self, item, spider):
        # 在这里执行将数据写入MongoDB的操作
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        # 在Spider关闭时关闭MongoDB连接
        self.client.close()
