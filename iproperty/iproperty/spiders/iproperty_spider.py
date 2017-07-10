import scrapy, logging, re, time
from scrapy.exceptions import CloseSpider
from iproperty.items import *

class ToolsdepotSpider(scrapy.Spider):
    name = 'iproperty'
    allowed_domain = ['www.iproperty.com.my']
    start_urls = ['https://www.iproperty.com.my/buy/kuala-lumpur/?sby=pdz&page=1', 'https://www.iproperty.com.my/buy/selangor/?sby=pdz&page=1']
    base_url = 'https://www.iproperty.com.my'
    close_down = False

    def parse(self, response):
        # logging.warning("Parse listing page: {}".format(response.url))
        all_links = list(set([x for x in response.css("ul.serp-listing-content a::attr(href)").extract()
                              if 'javascript:' not in x and 'ad.doubleclick' not in x and '/realestateagent/' not in x]))
        for link in all_links:
            if 'newlaunch.iproperty.com.my' in link:
                pass
            else:
                follow = "{}{}".format(self.base_url, link)
                request = scrapy.Request(follow, callback=self.parse_item_page)
                yield request


        # next page if any
        has_next = True
        for x in response.css("li.button a.disabled ::text").extract():
            if x == 'Next':
                has_next = False
                break

        if has_next:
            buttons = response.css("li.button a::attr(href)").extract()
            if len(buttons) > 0:
                next_page = buttons[-1]
                request = scrapy.Request("{}{}".format(self.base_url, next_page), callback=self.parse)
                yield request


    def parse_item_page(self, response):
        if self.close_down:
            raise CloseSpider()
        item = IpropertyItem()
        item['url'] = response.url
        item['scraped_date'] = time.strftime("%Y-%m-%d %H:%M:%S")

        # categories
        # pre-filled with None
        for x in xrange(1, 7):
            item['cat_{}'.format(x)] = None
        categories = [x for x in response.css("div.breadcrumbs-ld a::text").extract() if x != 'Home']
        for index, cat in enumerate(categories):
            if index > 5:
                raise CloseSpider("Category tree too long: {}".format(','.join(categories)))

            item['cat_{}'.format(index + 1)] = cat


        # unique ID
        result = re.search(r'.+-(\d+)$', response.url)
        if result:
            item['unique_id'] = result.group(1)


        # title
        item['title'] = next(iter(response.css("h1.main-title::text").extract()), '')
        if item['title'][-3:] == '...':
            item['title'] = next(iter(response.css("title ::text").extract()), '')

        # price
        item['price'] = next(iter(response.css("h2.price::text").extract()), '').replace('RM', '').replace(',', '').strip()

        # address
        item['address'] = next(iter(response.css(".building-info-one h2::attr(title)").extract()), '')

        # item details
        details = {}
        for d in response.css("ul.infos>li::text").extract():
            if ':' not in d:
                details.setdefault('facility', []).append(d.strip())
            else:
                splitted = d.split(' : ')
                if len(splitted) == 2:
                    details[splitted[0].strip()] = splitted[1].strip()

        # bedroom
        if 'Bedrooms' in details:
            item['bedroom'] = details['Bedrooms']
        else:
            item['bedroom'] = next(iter(response.css(".ld_mis_detail p.room span.bedroom::attr(title)").extract()), '').replace('Bedrooms', '').strip()

        # bathroom
        if 'Bathrooms' in details:
            item['bathroom'] = details['Bathrooms']
        else:
            item['bathroom'] = next(iter(response.css(".ld_mis_detail p.room span.bathroom::attr(title)").extract()), '').replace('Bathrooms', '').strip()

        item['carpark'] = next(iter(response.css(".ld_mis_detail p.room span.garage::attr(title)").extract()), '').replace('Car parks', '').strip()
        item['agent_name'] = next(iter(response.css("#agent-info .name a::text").extract()), '')
        item['agent_url'] = next(iter(response.css("#agent-info .name a::text").extract()), '')
        item['agent_phone'] = next(iter(response.css("#agentPhone::attr(value)").extract()), '')
        item['images'] = list(set(response.css("ul.gallery a::attr(href)").extract()))
        item['property_type'] = details.get('Property Type:', '')
        item['tenure'] = details.get('Tenure', '')
        item['land_area'] = details.get('Land Area', '')
        item['builtup'] = details.get('Built-Up', '')
        item['occupancy'] = details.get('Occupancy', '')
        item['furnishing'] = details.get('Furnishing', '')
        item['posted_date'] = details.get('Posted Date', '')
        item['facing_direction'] = details.get('Facing Direction', '')
        item['facility'] = details.get('facility', [])
        item['description'] = ' '.join([x for x in response.css("div.detail-info-wide ::text").extract() if x.strip() != ''])\
            .replace("\n", ' ').replace("\r", " ").replace("  ", " ")

        # expired
        expired = False
        for tag in response.css("h6 ::text").extract():
            if 'expired listing' in tag.lower():
                expired = True
                break
        item['expired'] = expired

        yield item