import psycopg2, time, psycopg2.extras
from scrapy.exceptions import DropItem
from datetime import datetime
import logging

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class PostgreSQLPipeline(object):

    conn = None
    conn_str = None
    cur = None
    today_str = ""
    crawler = None

    def __init__(self, conn_str, crawler):
        self.conn_str = conn_str
        self.today_str = time.strftime("%Y-%m-%d")
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            conn_str=crawler.settings.get('PGSQL_CONN'),
            crawler=crawler,
        )

    def open_spider(self, spider):
        self.conn = psycopg2.connect(self.conn_str)
        self.conn.set_session(autocommit=True)
        self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def close_spider(self, spider):
        self.cur.close()

    def process_item(self, item, spider):
        # try:
            # select from DB
            if item['unique_id'] == '' or item['unique_id'] is None:
                raise DropItem("unique_id is empty")

            # clean update data
            item['builtup'] = item['builtup'].replace(',', '').replace("sq. ft.", "").strip()

            # check row existence
            self.cur.execute("""SELECT * FROM listing_data WHERE unique_id = %s""", (item['unique_id'],))
            row = self.cur.fetchone()
            if row is None:
                listing_id = self.insert_item(item)
            else:
                # compare changes
                listing_id = row['id']
                self.update_changes(row, item)

            # update today's price
            self.update_price(listing_id, item)
        # except (Exception, psycopg2.DatabaseError) as error:
        #     spider.close_down = True
        #     raise error

    def insert_item(self, item):
        query = """INSERT INTO listing_data (
                        url,
                        cat_1,
                        cat_2,
                        cat_3,
                        cat_4,
                        cat_5,
                        cat_6,
                        expired,
                        unique_id,
                        title,
                        price,
                        address,
                        bedroom,
                        bathroom,
                        carpark,
                        agent_name,
                        agent_url,
                        agent_phone,
                        images,
                        property_type,
                        tenure,
                        land_area,
                        builtup,
                        occupancy,
                        furnishing,
                        posted_date,
                        facing_direction,
                        facility,
                        description
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s
                    ) RETURNING id"""
        self.cur.execute(query, (
            item["url"],
            item["cat_1"],
            item["cat_2"],
            item["cat_3"],
            item["cat_4"],
            item["cat_5"],
            item["cat_6"],
            item["expired"],
            item["unique_id"],
            item["title"],
            item["price"],
            item["address"],
            item["bedroom"],
            item["bathroom"],
            item["carpark"],
            item["agent_name"],
            item["agent_url"],
            item["agent_phone"],
            item["images"],
            item["property_type"],
            item["tenure"],
            item["land_area"],
            item['builtup'],
            item["occupancy"],
            item["furnishing"],
            datetime.strptime(item["posted_date"], "%d/%m/%Y").strftime("%Y-%m-%d"),
            item["facing_direction"],
            item["facility"],
            item["description"],
        ))
        new_id = self.cur.fetchone()[0]
        return new_id

    def update_changes(self, row, item):
        differences = []
        skip_fields = ['scraped_date', 'unique_id', 'posted_date', 'description']
        for key, val in row.iteritems():
            if key in item and key not in skip_fields:
                if not self.is_identical(val, item[key]):
                    differences.append({
                        'field': key,
                        'old_val': row[key],
                        'new_val': item[key],
                    })

        query = """INSERT INTO listing_changes (listing_id, date_capture, field, old_value, new_value)
                    VALUES (%s, %s, %s, %s, %s)"""
        for diff in differences:
            self.cur.execute(query, (row['id'], self.today_str, diff['field'],
                                     diff['old_val'], diff['new_val'],))

        #update main row
        if len(differences) > 0:
            query = """UPDATE listing_data
                        SET
                            url = %s,
                            cat_1 = %s,
                            cat_2 = %s,
                            cat_3 = %s,
                            cat_4 = %s,
                            cat_5 = %s,
                            cat_6 = %s,
                            expired = %s,
                            unique_id = %s,
                            title = %s,
                            price = %s,
                            address = %s,
                            bedroom = %s,
                            bathroom = %s,
                            carpark = %s,
                            agent_name = %s,
                            agent_url = %s,
                            agent_phone = %s,
                            images = %s,
                            property_type = %s,
                            tenure = %s,
                            land_area = %s,
                            builtup = %s,
                            occupancy = %s,
                            furnishing = %s,
                            posted_date = %s,
                            facing_direction = %s,
                            facility = %s,
                            description = %s
                        WHERE id = %s"""
            self.cur.execute(query, (
                item["url"],
                item["cat_1"],
                item["cat_2"],
                item["cat_3"],
                item["cat_4"],
                item["cat_5"],
                item["cat_6"],
                item["expired"],
                item["unique_id"],
                item["title"],
                item["price"],
                item["address"],
                item["bedroom"],
                item["bathroom"],
                item["carpark"],
                item["agent_name"],
                item["agent_url"],
                item["agent_phone"],
                item["images"],
                item["property_type"],
                item["tenure"],
                item["land_area"],
                item['builtup'],
                item["occupancy"],
                item["furnishing"],
                datetime.strptime(item["posted_date"], "%d/%m/%Y").strftime("%Y-%m-%d"),
                item["facing_direction"],
                item["facility"],
                item["description"],
                row['id']
            ))

    def update_price(self, listing_id, item):
        query = "INSERT INTO price_data (listing_id, date_capture, price) VALUES (%s, %s, %s)"
        self.cur.execute(query, (listing_id, self.today_str, item['price'],))

    def is_identical(self, data1, data2):
        if str(data1).decode('utf8', 'ignore') == str(data2).decode('utf8', 'ignore'):
            return True
        elif isinstance(data1, list) and isinstance(data2, list):
            not_in_a = [x for x in data1 if x not in data2]
            not_in_b = [x for x in data2 if x not in data1]
            if len(not_in_a) == 0 and len(not_in_b) == 0:
                return True
        else:
            try:
                f1 = float(str(data1))
                f2 = float(str(data2))
                if f1 - f2 == 0:
                    return True
            except Exception:
                return False

        return False
