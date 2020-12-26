import re

import nltk
import scrapy
from fake_useragent import UserAgent


class DramalistSpider(scrapy.Spider):
    name = 'dramalist'
    custom_settings = {
        'FEEDS': {
            'drama.json': {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 4
            }
        },
        'LOG_LEVEL': "INFO",
        "LOG_FILE": "drama.log"
    }

    def __init__(self):
        # Generating fake user agent that will be included in the headers
        ua = UserAgent()
        user_agent = ua.chrome
        self.headers = {"user-agent": user_agent}
    
    def start_requests(self):

        start_url = "https://mydramalist.com/shows/top"
        yield scrapy.Request(start_url, headers=self.headers, callback=self.parse)

    def parse(self, response):

        MAX_PAGES = self.get_max_page(response)
        for i in range(1, MAX_PAGES + 1):
            url = "https://mydramalist.com/shows/top?page=" + str(i)
            yield scrapy.Request(url, headers=self.headers, 
                                callback=self.scrap)
    
    def get_max_page(self, response):

        max_page = response.css(".last > a::attr(href)").get()
        max_page = re.search(r"page=(\d+)", max_page).group(1)
        max_page = int(max_page)
        
        return max_page

    def get_drama_name(self, response):

        name = response.css("title::text").get()
        name = name.replace(" - MyDramaList", "")

        return name

    def processing_synopsis(self, content):

        content = content.replace("\n", " ")
        content = re.sub(r"\s+", " ", content)

        return content

    def get_drama_synopsis(self, response):

        xpath = "//div[@class='show-synopsis']//span/text()"
        synopsis = response.xpath(xpath).getall()
        synopsis = " ".join(synopsis)
        synopsis = self.processing_synopsis(synopsis)

        return synopsis

    def get_user_rating(self, response):

        rating = response.css(".deep-orange::text").get()
        if rating != "N/A":
            rating = float(rating)
        else:
            rating = None

        return rating

    def get_nb_rating(self, response):

        xpath = "//div[@class='hfs']/text()"
        text = response.xpath(xpath).getall()
        text = [x for x in text if "user" in x]
        if text:
            text = text[0]
        else:
            return 0
        regex_pattern = r"(\d+(?:\,\d+)*) user"
        nb_rating = re.search(regex_pattern, text).group(1)
        nb_rating = nb_rating.replace(",", "")
        nb_rating = int(nb_rating)

        return nb_rating

    def get_nb_reviews(self, response):

        xpath = "//div[@class='hfs'][contains(., 'Reviews:')]/a/text()"
        text = response.xpath(xpath).get()
        nb_reviews = re.search(r'(\d*) user', text).group(1)
        nb_reviews = int(nb_reviews)

        return nb_reviews

    def duration_to_minutes(self, duration):

        try:
            nb_hours = re.search(r"(\d*) hr\.", duration).group(1)
            nb_hours = int(nb_hours)
        except AttributeError:
            nb_hours = 0
        hours_to_minute = nb_hours * 60

        initial_nb_minutes = re.search(r"(\d*) min\.", duration).group(1)
        initial_nb_minutes = int(initial_nb_minutes)
        total_nb_minutes = hours_to_minute + initial_nb_minutes

        return total_nb_minutes

    def get_duration(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[@class='inline duration']]/text()"
        duration = response.xpath(xpath).get()
        if duration is not None:
            duration = self.duration_to_minutes(duration)

        return duration

    def get_nb_episodes(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[contains(., 'Episodes')]]/text()"
        nb_episodes = response.xpath(xpath).get()
        nb_episodes = int(nb_episodes)

        return nb_episodes

    def get_country_origin(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[contains(., 'Country')]]/text()"
        nb_episodes = response.xpath(xpath).get().strip()

        return nb_episodes

    def get_ranking(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[contains(., 'Ranked')]]/text()"
        ranking = response.xpath(xpath).get().strip()
        ranking = ranking.replace("#", "")
        ranking = int(ranking)

        return ranking

    def get_popularity(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[contains(., 'Popularity')]]/text()"
        popularity = response.xpath(xpath).get().strip()
        popularity = popularity.replace("#", "")
        popularity = int(popularity)

        return popularity

    def get_nb_watchers(self, response):

        xpath = "//li[@class='list-item p-a-0'][child::b[contains(., 'Watchers')]]/text()"
        nb_watchers = response.xpath(xpath).get().strip()
        nb_watchers = nb_watchers.replace(",", "")
        nb_watchers = int(nb_watchers)

        return nb_watchers

    def get_streaming_platform(self, response):

        container_xpath = "//div[@class='box'][descendant::h3[contains" \
            "(., 'Where to Watch')]]"
        platforms_xpath = ".//a[@class='text-primary']/b/text()"
        container = response.xpath(container_xpath)
        platforms = container.xpath(platforms_xpath).getall()

        return platforms

    def get_genres(self, response):

        xpath = "//li[@class='list-item p-a-0 show-genres'][child::b" \
            "[contains(., 'Genres')]]/a/text()"
        genres = response.xpath(xpath).getall()

        return genres

    def get_tags(self, response):

        xpath = "//li[@class='list-item p-a-0 show-tags'][child::b" \
            "[contains(., 'Tags')]]/span/a/text()"
        tags = response.xpath(xpath).getall()

        return tags

    def get_main_roles(self, response):

        xpath = "//ul[preceding-sibling::h3[1][contains(., 'Main Role')]]/li//a" \
                "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        main_roles = response.xpath(xpath).getall()

        return main_roles

    def get_support_roles(self, response):

        xpath = "//ul[preceding-sibling::h3[1][contains(., 'Support Role')]]/li//a" \
                "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        support_roles = response.xpath(xpath).getall()

        return support_roles

    def get_guest_roles(self, response):

        xpath = "//ul[preceding-sibling::h3[1][contains(., 'Guest Role')]]/li//a" \
                "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        guest_roles = response.xpath(xpath).getall()

        return guest_roles

    def get_screenwriter(self, response):

        xpath = "//ul[preceding-sibling::h3[1][contains(., 'Screenwriter')]]/li//a" \
                "[@class='text-primary text-ellipsis' and contains(@href, 'people')]/b/text()"
        screenwriter = response.xpath(xpath).get()

        return screenwriter

    def get_director(self, response):

        xpath = "//ul[preceding-sibling::h3[1][contains(., 'Screenwriter')]]/li//a" \
                "[@class='text-primary text-ellipsis' and contains(@href, 'people')]/b/text()"
        director = response.xpath(xpath).get()

        return director

    def get_urls(self, response):

        urls = response.css(".text-primary.title > a::attr(href)").getall()
        urls = ["https://mydramalist.com" + x for x in urls]

        return urls
    
    def scrap(self, response):

        urls = self.get_urls(response)

        for url in urls:
            yield scrapy.Request(url, headers=self.headers,
                                callback=self.parse_main_tab)


    def parse_main_tab(self, response):
        
        try:
            self.check_drama(response)
        except NonDrama:
            return None
            
        data = {
            "name": self.get_drama_name(response),
            "synopsis": self.get_drama_synopsis(response),
            "duration_in_minutes": self.get_duration(response),
            "nb_episodes": self.get_nb_episodes(response),
            "country_origin": self.get_country_origin(response),
            "ratings": self.get_user_rating(response),
            "ranking": self.get_ranking(response),
            "popularity_rank": self.get_popularity(response),
            "nb_watchers": self.get_nb_watchers(response),
            "nb_ratings": self.get_nb_rating(response),
            "nb_reviews": self.get_nb_reviews(response),
            "streamed_on": self.get_streaming_platform(response),
            "genres": self.get_genres(response),
            "tags": self.get_tags(response),
            "mydramalist_url": response.url
        }
        casting_url = response.url + "/cast"
        yield scrapy.Request(casting_url, headers=self.headers,
                             callback=self.get_cast_members, meta={"data": data})

    def get_cast_members(self, response):

        main_tab_data = response.meta["data"]
        casting = {
            "screenwriter": self.get_screenwriter(response),
            "director": self.get_director(response),
            "main_roles": self.get_main_roles(response),
            "support_roles": self.get_support_roles(response),
            "guest_roles": self.get_guest_roles(response)
        }
        main_tab_data["casting"] = casting

        yield main_tab_data

    def check_drama(self, response):

        xpath = "//div[@class='box clear hidden-sm-down'][descendant::h3" \
                "[contains(., 'Details')]]//li[@class='list-item p-a-0']/b/text()"
        _type = response.xpath(xpath).get()
        _type = _type.replace(":", "")

        if _type != "Drama":
            message = f"Excluding the entry (url : {response.url}) as it is of " \
                        f"type '{_type}' instead of 'Drama'"
            raise NonDrama(message)

class NonDrama(Exception):

    def __init__(self, message):
        self.message = message

    
