import scrapy
from scrapy.http import FormRequest

class StoreSpider(scrapy.Spider):
    name = "store_spider"
    start_urls = ["https://stores.vijaysales.com/location/gujarat/ahmedabad"]

    def __init__(self):
        self.seen_stores = set()

    def parse(self, response):
        states = response.xpath("//*[@id='OutletState']/option/@value").getall()
        for state in states:
            if state:
                yield FormRequest.from_response(
                    response,
                    formdata={"state": state},
                    callback=self.parse_cities,
                    meta={"state": state},
                )

    def parse_cities(self, response):
        state = response.meta["state"]
        cities = response.xpath("//*[@id='OutletCity']/option/@value").getall()
        for city in cities:
            if city:
                yield FormRequest.from_response(
                    response,
                    formdata={"state": state, "city": city},
                    callback=self.parse_locations,
                    meta={"state": state, "city": city},
                )

    def parse_locations(self, response):
        state = response.meta["state"]
        city = response.meta["city"]
        locations = response.xpath("//*[@id='OutletLocality']/option/@value").getall()
        for location in locations:
            if location:
                yield FormRequest.from_response(
                    response,
                    formdata={"state": state, "city": city, "location": location},
                    callback=self.parse_data,
                    meta={"state": state, "city": city, "location": location},
                )

    def parse_data(self, response):
        state = response.meta["state"]
        city = response.meta["city"]
        location = response.meta["location"]
        cards = response.xpath("//div[@class='outlet-list']//div[@class='store-info-box']")
        for card in cards:
            store_name = card.xpath(".//ul/li//div[@class='info-text']/a/text()").get().strip()
            store_website = card.xpath(".//ul/li[@class='outlet-actions']//a[@class='btn btn-website']/@href").get()
            phone = card.xpath(".//ul/li[@class='outlet-phone']/div[@class='info-text']/a/text()").get(default='').strip()
            unique_store = (store_name, store_website, phone)

            if unique_store not in self.seen_stores:
                self.seen_stores.add(unique_store)
                yield {
                    "store_name": store_name,
                    "store_website": store_website,
                    "phone": phone,
                    "address": " ".join(card.xpath(".//ul/li[@class='outlet-address']//div[@class='info-text']/span//text()").getall()).strip(),
                    "near_by_place": card.xpath(".//ul[contains(@class,'outlet-detail')]/li[3]/div[@class='info-text']//text()").get(default='').strip(),
                    "location": location,
                    "city": city,
                    "state": state,
                    "outlet_timing": card.xpath(".//ul/li[@class='outlet-timings']//div[@class='info-text']/span//text()").get(default='').strip(),
                    "map": card.xpath(".//ul/li[@class='outlet-actions']//a[@class='btn btn-map']/@href").get(),
                }