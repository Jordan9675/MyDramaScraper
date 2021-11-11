import logging
import re

import scrapy
from fake_useragent import UserAgent


class DramalistSpider(scrapy.Spider):
    name = 'dramalist'
    MAX_PAGES = 250

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Generating fake user agent that will be included in the headers
        ua = UserAgent()
        user_agent = ua.chrome
        self.headers = {"user-agent": user_agent}
        # Setting an instance variable that enables/disables the insert Pipeline
        if kwargs.get("sql", "").lower() == "true":
            logging.info("Insertion in MySQL enabled")
            self.sql = True
        else:
            logging.info("Insertion in MySQL disabled")
            self.sql = False

    def start_requests(self):
        """
        Method used as a callback to the scrapy Request sent within the
        start_requests method. Through this method, we navigate through all the
        pages of the top shows.

        Args:
            response (scrapy.http.response): Response from the request made
            within start_requests

        Yields:
            scrapy.Request: Request made to each page of the top shows.
        """
        for i in range(1, self.MAX_PAGES + 1):
            url = "https://mydramalist.com/shows/top?page=" + str(i)
            yield scrapy.Request(url, headers=self.headers,
                                 callback=self.scrap)

    def get_drama_name(self, response):
        """
        Getting the name of the drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            str: name of the drama
        """
        name = response.css("title::text").get()
        name = name.replace(" - MyDramaList", "")

        return name

    def processing_synopsis(self, content):
        """
        Method that cleans the synopsis that is retrieved. We are replacing
        breaklines as well as extra spaces

        Args:
            content (str): content (synopsis) to clean

        Returns:
            str: cleaned content
        """
        content = content.replace("\n", " ")
        content = re.sub(r"\s+", " ", content)

        return content

    def get_drama_synopsis(self, response):
        """
        Retrieving the synopsis of the drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            str: Synopsis
        """
        xpath = "//div[@class='show-synopsis']//span/text()"
        synopsis = response.xpath(xpath).getall()
        synopsis = " ".join(synopsis)
        synopsis = self.processing_synopsis(synopsis)

        return synopsis

    def get_user_rating(self, response):
        """
        Retrieving the drama's rating

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            float: Drama's rating. Equals to None if not existing.
        """
        rating = response.css(".deep-orange::text").get()
        try:
            return float(rating)
        except ValueError:
            return None

    def get_nb_rating(self, response):
        """
        Retrieving the number of users that have rated the drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: number of users
        """
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
        """
        Retrieving the number of reviews written by users

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: number of reviews written
        """
        xpath = "//div[@class='hfs'][contains(., 'Reviews:')]/a/text()"
        text = response.xpath(xpath).get()
        nb_reviews = re.search(r'(\d*) user', text).group(1)
        nb_reviews = int(nb_reviews)

        return nb_reviews

    def duration_to_minutes(self, duration):
        """
        Method that allows us to convert the duration given by MyDramaList to
        a total number of minutes

        Args:
            duration (str): Duration of format x hr. y min.

        Returns:
            int: Number of minutes
        """
        try:
            nb_hours = re.search(r"(\d*) hr\.", duration).group(1)
            nb_hours = int(nb_hours)
        except AttributeError:
            nb_hours = 0
        hours_to_minute = nb_hours * 60

        initial_nb_minutes = re.search(r"(\d*) min\.", duration).group(1)
        initial_nb_minutes = int(initial_nb_minutes)

        return hours_to_minute + initial_nb_minutes

    def get_duration(self, response):
        """
        Retieving the duration of each episode of a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: Duration of an episode in minutes
        """
        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[@class='inline duration']]/text()"
        )
        duration = response.xpath(xpath).get()
        if duration is not None:
            duration = self.duration_to_minutes(duration)

        return duration

    def get_nb_episodes(self, response):
        """
        Retrieving a drama's number of episodes

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: number of episodes
        """
        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[contains(., 'Episodes')]]/text()"
        )
        nb_episodes = response.xpath(xpath).get()

        return int(nb_episodes)

    def get_country_origin(self, response):
        """
        Retrieving the country of origin of a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            str: Country of origin
        """
        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[contains(., 'Country')]]/text()"
        )

        return response.xpath(xpath).get().strip()

    def get_ranking(self, response):
        """
        Retrieve the rank of the drama based on user's rating

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: Rank of the drama on MyDramaList
        """

        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[contains(., 'Ranked')]]/text()"
        )
        ranking = response.xpath(xpath).get().strip()
        ranking = ranking.replace("#", "")

        return int(ranking)

    def get_popularity(self, response):
        """
        Retrieving the popularity (express as a rank) of a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: Popularity rank
        """
        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[contains(., 'Popularity')]]/text()"
        )
        popularity = response.xpath(xpath).get().strip()
        popularity = popularity.replace("#", "")

        return int(popularity)

    def get_nb_watchers(self, response):
        """
        Retrieve the number of users that are or have watched a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            int: number of watchers
        """
        xpath = (
            "//li[@class='list-item p-a-0']"
            "[child::b[contains(., 'Watchers')]]/text()"
        )
        nb_watchers = response.xpath(xpath).get().strip()
        nb_watchers = nb_watchers.replace(",", "")

        return int(nb_watchers)

    def get_streaming_platform(self, response):
        """
        Retrieving the list of platofmrs that are broadcasting a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            list: list of platforms
        """
        container_xpath = (
            "//div[@class='box']"
            "[descendant::h3[contains(., 'Where to Watch')]]"
        )
        platforms_xpath = ".//a[@class='text-primary']/b/text()"
        container = response.xpath(container_xpath)
        
        return container.xpath(platforms_xpath).getall()

    def get_genres(self, response):
        """
        Retrieving the genres associated to a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            list: list of genres
        """
        xpath = (
            "//li[@class='list-item p-a-0 show-genres'][child::b"
            "[contains(., 'Genres')]]/a/text()"
        )
        return response.xpath(xpath).getall()

    def get_tags(self, response):
        """
        Retrieving the tags associated to a given drama

        Args:
            response (scrapy.http.response): Response from a scrapy.Request 
            made to a drama's page

        Returns:
            list: list of tags
        """
        xpath = (
            "//li[@class='list-item p-a-0 show-tags'][child::b"
            "[contains(., 'Tags')]]/span/a/text()"
        )

        return response.xpath(xpath).getall()

    def get_main_roles(self, response):
        """
        Retrieving the list of actors that have a main role in a given drama

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to a drama's cast page

        Returns:
            list: list of actors
        """
        xpath = (
            "//ul[preceding-sibling::h3[1][contains(., 'Main Role')]]/li//a" 
            "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        )

        return response.xpath(xpath).getall()

    def get_support_roles(self, response):
        """
        Retrieving the list of actors that have a support role in a given drama

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to a drama's cast page

        Returns:
            list: list of actors
        """
        xpath = (
            "//ul[preceding-sibling::h3[1][contains(., 'Support Role')]]/li//a"
            "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        )

        return response.xpath(xpath).getall()

    def get_guest_roles(self, response):
        """
        Retrieving the list of actors that have a guest role in a given drama

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to a drama's cast page

        Returns:
            list: list of actors
        """
        xpath = (
            "//ul[preceding-sibling::h3[1][contains(., 'Guest Role')]]/li//a"
            "[@class='text-primary' and contains(@href, 'people')]/b/text()"
        )

        return response.xpath(xpath).getall()

    def get_screenwriter(self, response):
        """
        Retrieving the screenwriter of a given drama

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to a drama's cast page

        Returns:
            str: name of the screenwriter
        """
        xpath = (
            "//ul[preceding-sibling::h3[1][contains(., 'Screenwriter')]]/li//a"
            "[@class='text-primary text-ellipsis' and "
            "contains(@href, 'people')]/b/text()"
        )

        return response.xpath(xpath).getall()

    def get_director(self, response):
        """
        Retrieving the director of a given drama

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to a drama's cast page

        Returns:
            str: name of the director
        """
        xpath = (
            "//ul[preceding-sibling::h3[1][contains(., 'Director')]]/li//a"
            "[@class='text-primary text-ellipsis' and "
            "contains(@href, 'people')]/b/text()"
        )

        return response.xpath(xpath).getall()

    def get_urls(self, response):
        """
        Retrieving a list of urls corresponding to the drama displayed on a
        given page from the top shows

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to one of the top show's page

        Returns:
            list: list of urls
        """
        urls = response.css(".text-primary.title > a::attr(href)").getall()

        return ["https://mydramalist.com" + x for x in urls]

    def scrap(self, response):
        """
        Callback method used when requesting one of the top show's page

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to one of the top show's page

        Yields:
            scrapy.Request: Request to the url associated to a given drama
        """
        urls = self.get_urls(response)

        for url in urls:
            yield scrapy.Request(
                url, 
                headers=self.headers,
                callback=self.parse_main_tab)

    def parse_main_tab(self, response):
        """
        Callback method used within 'scrap' that retrieves all the information
        of a given drama (except information regarding the casting). This method
        then yields a scrapy.Request to the cast tab using and using the
        get_cast_members callback method.

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to the page of a given drama

        Yields:
            scrapy.Request: Scrapy Request to the cast tab.
        """
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
        """
        Callback method used to retrieve the cast members of a given drama. 

        Args:
            response (scrapy.Request): Response from a scrapy.Request 
            made to one of the top show's page

        Yields:
            dict: Cast members stored as value. The keys are corresponding to
            the type of role (main, support, guest)
        """
        main_tab_data = response.meta["data"]
        main_tab_data["screenwriter"] = self.get_screenwriter(response)
        main_tab_data["director"] = self.get_director(response)
        main_tab_data["main_roles"] = self.get_main_roles(response)
        main_tab_data["support_roles"] = self.get_support_roles(response)
        main_tab_data["guest_roles"] = self.get_guest_roles(response)

        yield main_tab_data
