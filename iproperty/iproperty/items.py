# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IpropertyItem(scrapy.Item):
    url = scrapy.Field()
    scraped_date = scrapy.Field()
    cat_1 = scrapy.Field()
    cat_2 = scrapy.Field()
    cat_3 = scrapy.Field()
    cat_4 = scrapy.Field()
    cat_5 = scrapy.Field()
    cat_6 = scrapy.Field()
    expired = scrapy.Field()
    unique_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    address = scrapy.Field()
    bedroom = scrapy.Field()
    bathroom = scrapy.Field()
    carpark = scrapy.Field()
    agent_name = scrapy.Field()
    agent_url = scrapy.Field()
    agent_phone = scrapy.Field()
    images = scrapy.Field()
    property_type = scrapy.Field()
    tenure = scrapy.Field()
    land_area = scrapy.Field()
    builtup = scrapy.Field()
    occupancy = scrapy.Field()
    furnishing = scrapy.Field()
    posted_date = scrapy.Field()
    facing_direction = scrapy.Field()
    facility = scrapy.Field()
    description = scrapy.Field()


class IpropertyNewlaunchItem(scrapy.Item):
    url = scrapy.Field()
    scraped_date = scrapy.Field()
    cat_1 = scrapy.Field()
    cat_2 = scrapy.Field()
    cat_3 = scrapy.Field()
    cat_4 = scrapy.Field()
    cat_5 = scrapy.Field()
    cat_6 = scrapy.Field()
    unique_id = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    listing_price = scrapy.Field()
    quikpro_no = scrapy.Field()
    property_type = scrapy.Field()
    land_title = scrapy.Field()
    tenure = scrapy.Field()
    built_up = scrapy.Field()
    land_area = scrapy.Field()
    total_units = scrapy.Field()
    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    completion_date = scrapy.Field()
    posted_date = scrapy.Field()
    brochure = scrapy.Field()
    facility = scrapy.Field()
    property_details = scrapy.Field()
