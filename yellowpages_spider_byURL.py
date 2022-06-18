import scrapy
from scrapy.crawler import CrawlerProcess
from random import randrange

URLs = [
    "https://www.yellowpages.com/search?search_terms=resturants&geo_location_terms=Minneapolis%2C+MN",
]


class Yellowpages(scrapy.Spider):
    name = "yellowpages"

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Data.csv',
    }

    def start_requests(self):
        for url in URLs:
            yield scrapy.Request(url=url,
                             callback=self.parse, dont_filter=True,
                             headers={
                                 'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                               "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                             },
                             )

    def parse(self, response):
        data = response.css("div.search-results.organic > div")
        companies = data.css("a.business-name::attr(href)").extract()
        for company in companies:
            yield scrapy.Request(
                url="https://www.yellowpages.com" + company,
                callback=self.parse2, dont_filter=True,
                headers={
                    'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                  "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                },
                )

        nextPage = response.css("li > a.next::attr(href)").extract_first()
        if nextPage:
            yield scrapy.Request(
                url="https://www.yellowpages.com" + nextPage,
                callback=self.parse, dont_filter=True,
                headers={
                    'USER-AGENT': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, "
                                  "like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                },
                )

    def parse2(self, response):
        name = response.css("h1.business-name::text").extract_first()
        phone = response.css("a.phone > strong::text").extract_first()
        address1 = response.css("span.address > span::text").extract_first()
        address2 = response.css("span.address::text").extract_first()

        if address2:
            zipCode = address2.split(" ")[-1].strip()
        else:
            zipCode = ""

        if address1 and address2:
            address = address1 + ", " + address2
        else:
            address = "N/A"

        website = response.css("a.website-link::attr(href)").extract_first()
        email = response.css("a.email-business::attr(href)").extract_first()

        if not website:
            website = "N/A"
        if not email:
            email = "N/A"

        email = email.replace("mailto:", "")

        yield {
            "Name": name,
            "Phone": phone,
            "Email": email,
            "Website": website,
            "Zip Code": zipCode,
            "Address": address,
        }



process = CrawlerProcess()
process.crawl(Yellowpages)
process.start()