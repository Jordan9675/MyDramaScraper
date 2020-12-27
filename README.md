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

## Insert in MySQL

This scrapy project comes with a pipeline allowing to insert the results in a MySQL database. 

### How to enable the pipeline ?

The pipeline is enabled by default but won't insert anything unless it's asked to. 

It does require a small extra loading time when initializing the spider so I do recommend disabling it by emptying the `ITEM_PIPELINES` in the `settings.py` file located in the Scrapy project. It should then look like this : 

```
ITEM_PIPELINES = {}
```

### Where to provide the credentials ? 

The credentials of the database are currently provided to the pipeline as environmental variables through a hidden `.env` file which is loaded using the [dotenv](https://pypi.org/project/python-dotenv/) python package.

Here is an example of how the file looks like :

```
HOST=xxxxxxxxxxxxx
DB=xxxxxxxxxxxxx
USERNAME=xxxxxxxxxxxxx
PASSWORD=xxxxxxxxxxxxx
```

The name of the environmental can be changed within this file but don't forget also to change them in the `db_connection` method from the `InsertItem` pipeline.

For simplicity, you could also hardcode your credentials in the `db_connection` method but this is **not recommended**.

### How to ask the pipeline to insert the records ?

Even though the pipeline is enabled by default, it won't insert your records unless you ask him for it by specifying an argument when launching the spider.

To do so, you could run something like :

`scrapy crawl dramalist -a sql=True`

> Please note that here, the value of the sql argument is True but could be whatever as long as it is not an empty string.

### What columns should I create in my DB ?

Currently, the insertion is based on hardcoded column names that are arbitrarily chosen.

They can be found in the `query` variable (which refers to the SQL query) within the `process_item` method in the `InsertItem` pipeline.

Feel free to name them as you wish and to process the data the way it suits to your needs. However, don't forget to assign the `VARCHAR` or `JSON` type to the columns that should store data of type `list`.

If changing the predetermined names of the columns, please ensure that the order is still corresponding to the order of the keys from the item returned by the scrapy spider. 

The insertion is here based on values wrapped into a tuple. The order of the values provided in the tuple should be corresponding to the column name they are associated to. 

For example, `name` is provided as the first column to be filled which implies that its value will be equal to the first element of the tuple that will be provided. 

When changing the name of the columns and their order, keep in mind that the order of the values provided as a tuple should be changed correspondingly too.
## Motivation

This project is the brick of another upcoming project. Indeed, we are motivated in scraping information on MyDramaList so that we can later create a **drama recommandation system** based on the user's taste in terms of drama. 

We are mainly interested in retrieving information that could be relevant when creating such a system which explains why we decided not to retrieve some types of information from MyDramaList.

## To do

- [x] Add a requirements.txt file
- [x] Add docstrings
- [ ] Implement some user arguments :
    - [ ] Maximum pages to scrape
    - [ ] Minimum rating
    - [ ] Date range
- [ ] Scrape information located in the statistics tab of the drama's page
- [ ] Creating a spider to retrieve information about the actors
- [x] Implement a pipeline to allow insertion into MySQL databases

## Contact

If there is any missing information that you would be interested in retrieving through the spiders, please send me an e-mail at jordan.vuong96@gmail.com.