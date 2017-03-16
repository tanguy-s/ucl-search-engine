import re
import time
import random
import urllib
import json
import requests
import numpy as np
from bs4 import BeautifulSoup

from selenium import webdriver

import fnmatch
from lxml import html

from django.core.management.base import BaseCommand, CommandError

from engine.models import WebPage
from engine.tasks import crawler_v2



# queries = ["prospective students",
# "MSc Busics",
# "Geometry",
# "Danail Stoyanov",
# "Gabriel Brostow",
# queries = ["Robot vision and navigation",
# "logic semantics and verification",
# "statistical natural language processing",
# "cryptanalysis",
# "machine learning",
# "mahcin learning",
# "learning machines",
# "learn machine",
#  "Business Analytics",
#  "Buisness Analytic",
#  "Busines Analytic"]

queries = ['Computer Science','Computer','Computer Room','Computer Science Department','Jun Wang',
               'Emine Yilmaz','Machine Learning', 'Web Science and Big Data Analytics',
               'Data Science', 'Information Retrieval and Data Mining', 'Web Economics', 'Supervised Learning',
               'Applied Machine Learning', 'Statistical Natural Language Processing', 'Sebastian Riedel',
               'MsC Computer Science', 'Research', 'Computer Science Research', 'Admissions', 'Computer Science BsC',
               'Advanced Topics in Machine Learning', 'Deep Mind', 'Google', 'Thesis', 'Thesis Projects',
               'Courses', 'Fees', 'Mark Herbster', 'David Barber', 'computer science phd', 'research projects',
               'Computer science department', 'Machine Learning Syllabus', 'Deep Learning', 'Computer Science courses',
               'Timetable', 'Exams', 'Exam timetable', 'Computer Science facilities', 'Computer hub', 'Underground station',
               'Microsoft Research', 'Euston Square', 'London East Campus', 'Roberts Engineering Building',
               'Main Quad', 'Twitter Botnets', 'Starcraft playing AI', 'AlphaGo', 'Philip Treleaven', 'Bloomsbury',
               'Phineas', 'Weekend activities', 'Computer Science Staff', 'Mathematics Staff', 'Financial Computation',
               'regression trees', 'Distribute Systems and Security', 'DSS', 'Brad Karp', 'Stanford', 'Airports',
               'traffic control', 'Self driving cars', 'Uber', 'Insurance', 'Risk prediction', 'Bursary', 'Grants',
               'Library', 'Group study rooms', 'moodle', 'portico', 'Tottenham Court Road', 'Holborn', 'Growing Trees',
               'Adaboost', 'UCL staff', 'password reset', 'The art of generating a test set']

class Command(BaseCommand):

    def handle(self, *args, **options):
        #page = requests.get('https://www.google.co.uk/search?q=site%3Acs.ucl.ac.uk#q=site:cs.ucl.ac.uk&start=10')

        with open('google_results.json', 'r') as f:
            gg_res = json.load(f)

        browser = webdriver.Chrome('/Users/tanguyserrat/Documents/ucl/IRDM/uclse/chromedriver')

        res_dict = {}
        for query in queries: # From bernardo Branco

            if query not in gg_res:
                all_links = list()

                for i in range(0, 100, 10):
                    time.sleep(random.uniform(2, 8))

                    url = 'https://www.google.co.uk/search?q='+ urllib.parse.quote_plus(query) +'%20site%3Acs.ucl.ac.uk&filter=0&start=' + str(i)
                    browser.get(url)
                    page = browser.page_source
                    doc = html.fromstring(page)
                    links = doc.xpath('//a[@href]')
                    for link in links:
                        href = link.attrib['href']    
                        if (fnmatch.fnmatch(href, '*cs.ucl.ac.uk*') and 
                            not fnmatch.fnmatch(href, '*google*') and 
                            fnmatch.fnmatch(href, '*http*')):
                            all_links.append(href)

                res_dict[query] = all_links
                print(json.dumps(res_dict))
                print('')
        print(json.dumps(res_dict))


        # for link in links:
        #     print(link.attrib)
        #     try:
        #         href = link.attrib['data-href']
        #     except KeyError:
        #         pass
        #     else:
        #         print(href)
        # soup = BeautifulSoup(page.content)
        
        # links = soup.findAll('a')
        # for link in  soup.find_all('a',href=re.compile('(?<=/url\?q=)(htt.*://.*)')):
        #     print(re.split(':(?=http)',link['href'].replace('/url?q=','')))