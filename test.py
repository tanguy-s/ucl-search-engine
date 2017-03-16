import time

import pymongo
from pymongo import MongoClient


from engine.crawler import get_page
#from engine.crawler import Crawler, CrawlerProcess

start_time = time.time()
res1 = get_page('http://www.ucl.ac.uk')
print(res1[2]['content_type'])
