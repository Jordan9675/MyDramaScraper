import sys

import scrapy
from fake_useragent import UserAgent


class UserdramalistSpider(scrapy.Spider):
    name = 'userdramalist'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = self.generate_user_agent()
        self.users = self.retrieve_user_arguments(**kwargs)

    def generate_user_agent(self):
        ua = UserAgent()
        user_agent = ua.chrome
        headers = {"user-agent": user_agent}

        return headers
    
    def retrieve_user_arguments(self, **kwargs):
        if "users" in kwargs:
            users = kwargs.get("users").split(",")
            users = [user.strip() for user in users]
        else:
            sys.exit("No argument provided for the 'user' argument")
        return users

    def start_requests(self):
        base_url = "https://mydramalist.com/dramalist/{}/completed"
        for user in self.users:
            url = base_url.format(user)
            yield scrapy.Request(
                url, callback=self.parse, meta={"user": user}, headers=self.headers)
        
    def parse(self, response):
        rows = response.css("tbody > tr")
        for row in rows:
            data = {
                "title": self.get_title(row),
                "score": self.get_score(row),
                "user": response.meta["user"]
            }
            yield data

    def get_title(self, selector):
        title = selector.css(".title.text-primary span::text").get()
        return title

    def get_score(self, selector):
        score = selector.css(".score::text").get()
        score = int(float(score))

        return score
