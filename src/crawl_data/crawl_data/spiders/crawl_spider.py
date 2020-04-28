import scrapy
from scrapy.spiders import CrawlSpider
from ..items import CrawlDataItem
from scrapy.crawler import CrawlerProcess

class xsmn_spider(CrawlSpider):
    name = 'xsmn'

    custom_settings = {
        'FEED_URI': 'db/xsmn.json',
        'FEED_FORMAT' : 'json'
    }

    allowed_domains = ["xskt.com.vn"]

    start_urls = [
        "https://xskt.com.vn/xsmn/"
    ]

    def parse(self, response):
        data_resp = scrapy.Selector(response)
        
        table_index = 0
        while table_index < 7:           
            for i in range(2, 4 + 2):
                items = CrawlDataItem()

                if not data_resp.xpath("//table[@id='MN" + str(table_index) + "']/tr/th[{0}]/a/text()".format(i)):
                    break

                items['location'] = data_resp.xpath("//table[@id='MN" + str(table_index) + "']/tr/th[{0}]/a/text()".format(i)).extract_first()
                
                tmp_data = {}

                for j in range(2, 11):
                    tmp_reward = data_resp.xpath("//table[@id='MN" + str(table_index) + "']/tr[{0}]/td[1]/text()".format(j)).extract_first()
                    tmp_number = data_resp.xpath("//table[@id='MN" + str(table_index) + "']/tr[{0}]/td[{1}]//text()".format(j, i)).extract()
                    tmp_data[tmp_reward] = ", ".join(tmp_number)

                items['data'] = tmp_data

                yield items

            table_index = table_index + 1

class xsmt_spider(CrawlSpider):
    name = 'xsmt'

    custom_settings = {
        'FEED_URI': 'db/xsmt.json',
        'FEED_FORMAT' : 'json'
    }

    allowed_domains = ["xskt.com.vn"]

    start_urls = [
        "https://xskt.com.vn/xsmt/"
    ]

    def parse(self, response):
        data_resp = scrapy.Selector(response)
        
        table_index = 0
        while table_index < 7:           
            for i in range(2, 3 + 2):
                items = CrawlDataItem()
                
                if not data_resp.xpath("//table[@id='MT" + str(table_index) + "']/tr/th[{0}]/a/text()".format(i)):
                    break

                items['location'] = data_resp.xpath("//table[@id='MT" + str(table_index) + "']/tr/th[{0}]/a/text()".format(i)).extract_first()
                
                tmp_data = {}

                for j in range(2, 11):
                    tmp_reward = data_resp.xpath("//table[@id='MT" + str(table_index) + "']/tr[{0}]/td[1]/text()".format(j)).extract_first()
                    tmp_number = data_resp.xpath("//table[@id='MT" + str(table_index) + "']/tr[{0}]/td[{1}]//text()".format(j, i)).extract()
                    tmp_data[tmp_reward] = ", ".join(tmp_number)

                items['data'] = tmp_data

                yield items

            table_index = table_index + 1

class xsmb_spider(CrawlSpider):
    name = 'xsmb'

    custom_settings = {
        'FEED_URI': 'db/xsmb.json',
        'FEED_FORMAT' : 'json'
    }

    allowed_domains = ["xskt.com.vn"]

    start_urls = [
        "https://xskt.com.vn/xsmb/"
    ]

    def parse(self, response):
        data_resp = scrapy.Selector(response)
        
        table_index = 0
        while table_index < 7:           
            items = CrawlDataItem()

            location = data_resp.xpath("//table[@id='MB" + str(table_index) + "']/tr/th/h3/text()[2]").extract_first()
            location = location.strip("() ")

            items['location'] = location
                
            tmp_data = {}

            for j in range(2, 12):
                if j == 6 or j == 9:
                    continue;
                tmp_reward = data_resp.xpath("//table[@id='MB" + str(table_index) + "']/tr[{0}]/td/text()".format(j)).extract_first()

                if j == 2:
                    tmp_number = data_resp.xpath("//table[@id='MB" + str(table_index) + "']/tr[{0}]/td[2]/em/text()".format(j)).extract()
                else:
                    tmp_number = data_resp.xpath("//table[@id='MB" + str(table_index) + "']/tr[{0}]/td[2]/p/text()".format(j)).extract()

                tmp_number = ", ".join(tmp_number)
                tmp_number = tmp_number.replace(",", "")
                tmp_number = tmp_number.replace(" ", ", ")
                tmp_data[tmp_reward] = tmp_number

                items['data'] = tmp_data

            yield items

            table_index = table_index + 1


process = CrawlerProcess()
process.crawl(xsmn_spider)
process.crawl(xsmt_spider)
process.crawl(xsmb_spider)
process.start()