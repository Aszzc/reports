import scrapy
import sys
sys.path.append('..')

import config as cfg
import os

class MySpider(scrapy.Spider):
    name = cfg.SPIDER_NAME
    RUNNING_FLAG = []

    def start_requests(self):
        # today_date = cfg.now()
        # today_date = '2018-01-01'
        # init_date = '2017-01-01'
        today_date = os.environ.get('TODAY_DATE')
        init_date = os.environ.get('INIT_DATE')

        for task, url in cfg.APIs.items():
            page = 1
            self.RUNNING_FLAG = {task:True}
            
            while self.RUNNING_FLAG[task]:
                url = cfg.geturl(task, btime=init_date, etime=today_date, page=page)
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    meta= {'task':task},
                )
                page += 1

    def parse(self, response):
        datas = response.json()['data']
        task = response.meta['task']
        item = scrapy.Item()

        item.fields['task'] = scrapy.Field()

        for data in datas:
            item['task'] = task
            for key, value in data.items():
                item.fields[key] = scrapy.Field()
                item[key] = value
            yield item

        if len(datas) == 0:
            self.RUNNING_FLAG[task] = False
