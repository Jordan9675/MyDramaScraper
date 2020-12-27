# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import os

import mysql.connector
from dotenv import load_dotenv
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class InsertItem:

    def __init__(self):
        load_dotenv()
        self.db_connection()

    def db_connection(self):
        """
        Create a connection to the database
        """
        self.db = mysql.connector.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USERNAME"),
            passwd=os.getenv("PASSWORD"),
            database=os.getenv("DB")
        )
        self.cursor = self.db.cursor(dictionary=True)

    def convert_to_json_string(self, item):
        """
        Convert every value of format dictionary to a json string

        Args:
            item (dict): item returned by our Scrapy spider

        Returns:
            dict: Informations about a drama with JSON strings
        """
        for key in item:
            if isinstance(item[key], list):
                item[key] = json.dumps(item[key])

        return item

    def unescape_apostrophes(self, item):
        """
        Replace every single quote by double quotes to avoid any trouble
        during the SQL insertion

        Args:
            item (dict): item returned by our Scrapy spider

        Returns:
            dict: Informations about a drama with escaped single quotes
        """
        for key in item:
            if isinstance(item[key], str):
                item[key] = item[key].replace("'", "''")

        return item

    def process_item(self, item, spider):
        """
        Method that is performed on each item returned by our spider and which
        allows us to insert it into the DB

        Args:
            item (dict): item returned by our Scrapy spider
            spider (scrapy.Spider): Scrapy spider object
        """
        if spider.sql:
            query = "INSERT INTO drama (name, synopsis, duration, nb_episodes, " \
                    "country, rating, ranking, popularity_rank, nb_watchers, " \
                    "nb_ratings, nb_reviews, streamed_on, genres, tags, " \
                    "mydramalisturl, screenwriter, director, mainroles, " \
                    "supportingroles, guestroles) VALUES (%s, %s, %s, %s, %s, " \
                    "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            item = self.convert_to_json_string(item)
            item = self.unescape_apostrophes(item)
            values = tuple(item.values())
            self.cursor.execute(query, values)
            self.db.commit()