# Your Turn!
import logging
import time
import random
import csv
import requests
import sys
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
with open('data/kardashian_jenner_urls_jan_1_2024_to_july_31_2024_mediacloud.csv', 'r') as f:
    reader = csv.reader(f, delimiter=',')
    urls = [line[-1] for line in reader][1:]
    
logging.basicConfig(filename='kardashian_problems.log', encoding='utf-8',level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def get_people_in_article(url):
    """
    Given a URL (string) of a TMZ article, 
    return a list of the names of the people (as strings) whose TMZ pages are linked in the article. 
    Handle invalid URLs and logging.
    """
    people_in_article = []
    
    try:
        logging.info(f"Fetching the URL: {url}")
        res = requests.get(url)
        res.raise_for_status()  # Raises HTTPError for bad responses
        
        soup = BeautifulSoup(res.text, 'html.parser')
        logging.info("Successfully fetched and parsed the page.")
        for text_line in soup.find_all('p'):
            a_tags = text_line.find_all('a')
            for tag in a_tags:
                href = tag.get('href')
                if href and 'https://www.tmz.com/people/' in href:
                    person_name = href.split('/')[-2]
                    logging.debug(f"Found person: {person_name}")
                    people_in_article.append(person_name)

        logging.info(f"People found in article: {people_in_article}")
        return people_in_article

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the URL: {url} - {e}")
        return people_in_article 

lists_of_people = []
for url in random.sample(urls, 30):
    lists_of_people.append(get_people_in_article(url))
    time.sleep(7)
    
pickle.dump(lists_of_people, open('lists_of_people.pkl', 'wb'))