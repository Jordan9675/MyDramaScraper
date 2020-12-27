# MyDramaScraper

This repository provides a classic Scrapy project with a spider named **dramascraper** which allows one to scrap information about the dramas that are listed on [MyDramaList](https://mydramalist.com/).

## Quick start

To run the spider, first install the dependencies running : 

`pip install -r requirements.txt`

Then, navigate through the the scrapy project called dramascraper which is located in the root directory and from there, you can very simply run the spider by running : 

`scrapy crawl dramascraper`

## Data types

| Key                 	| Type       	| Description                                                	|
|---------------------	|------------	|------------------------------------------------------------	|
| name                	| String     	| Name of the drama                                          	|
| synopsis            	| String     	| Synopsis of the drama                                      	|
| duration_in_minutes 	| Integer    	| Duration of each episodes (in minutes)                     	|
| nb_episodes         	| Integer    	| Number of episodes                                         	|
| country_origin      	| String     	| Drama's country of origin                                  	|
| ratings             	| Float      	| Ratings from MyDramaList's users                           	|
| ranking             	| Integer    	| Ranking based on the ratings                               	|
| popularity_rank     	| Integer    	| Ranking based on the drama's popularity                    	|
| nb_watchers         	| Integer    	| Number of MyDramaList's users currently watching the drama 	|
| nb_ratings          	| Integer    	| Number of users that have rated the drama                  	|
| nb_reviews          	| Integer    	| Number of reviews written by MyDramaList's users           	|
| streamed_on         	| List       	| List of platforms on which the drama is broadcaster        	|
| genres              	| List       	| List of genres associated to the drama                     	|
| tags                	| List       	| List of tags associated to the drama                       	|
| mydramalist_url     	| String     	| URL of the drama on MyDramaList                            	|
| director             	| String 	    | Name of the drama's director        	                        |
| screenwriter          | String 	    | Name of the drama's screenwriter                              |
| main_roles            | List 	        | List of the actors having a main role in the drama          	|
| support_roles         | List 	        | List of the actors having a support role in the drama         |
| guest_roles           | List 	        | List of the actors having a guest role in the drama        	|

## Motivation

This project is the brick of another upcoming project. Indeed, we are motivated in scraping information on MyDramaList so that we can later create a **drama recommandation system** based on the user's taste in terms of drama. 

We are mainly interested in retrieving information that could be relevant when creating such a system which explains why we decided not to retrieve some types of information from MyDramaList.

## To do

- [ ] Add a requirements.txt file
- [x] Add docstrings
- [ ] Implement some user arguments :
    - [ ] Maximum pages to scrape
    - [ ] Minimum rating
    - [ ] Date range
- [ ] Scrape information located in the statistics tab of the drama's page
- [ ] Creating a spider to retrieve information about the actors
- [ ] Implement a pipeline to allow insertion into MySQL databases

## Contact

If there is any missing information that you would be interested in retrieving through the spiders, please send me an e-mail at jordan.vuong96@gmail.com.