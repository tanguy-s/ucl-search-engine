import time
import requests
from celery import shared_task
#from pymongo import MongoClient

from django.conf import settings

from engine.models import WebPage
from engine.crawler import get_page
from engine.forms import WebPageForm

import hashlib


@shared_task(ignore_result=True)
def crawler_v2(page_url):
    # Crawl URL
    page, created = WebPage.objects.get_or_create(url=page_url)
    if created or page.crawled == False:

        results = get_page(page.url)
        print('CRAWLING: ', page.url)
        print('CRAWLING STATUS: ', results[1])

        page_dict = {
            'raw_html': None,
            'status': 0,
            'content_type': None,
        }

        if results[0]:
            start_time_1 = time.time()
            resp = results[2]

            if 'html' in resp['content_type']:

                for out_link in resp['out_links']:
                    page_out, created_out = WebPage.objects.get_or_create(url=out_link)
                    if created:
                        crawler_v2.delay(page_out.url)

                page_dict['raw_html'] = resp['raw'] 
                print('CRAWLING TYPE: ', resp['content_type'])

            page_dict['content_type'] = resp['content_type']

        page_dict['status'] = results[1]

        page_form = WebPageForm(data=page_dict, instance=page)
        if page_form.is_valid():
            page = page_form.save()
            print('## Saved Page')
        else:
            print('## Error saving page')


@shared_task(ignore_result=True)
def update_url(page_url):
    # Crawl URL
    try:
        page = WebPage.objects.get(url=page_url)
    except:
        print('Page not found!')
        pass
    else:
        try:
            req = requests.get(page.url, stream=True, timeout=5)
            req.raise_for_status()
        except:
            print('Request error')
            pass
        else:
            page.url_update = req.url
            if page_url != req.url:
                page.save()
                print('## URL WAS DIFFERENT')
            else:
                print('## NOT DIFFERENT')


@shared_task(ignore_result=True)
def crawler_single(page_url):
    # Crawl URL
    page, created = WebPage.objects.get_or_create(url=page_url)
    if created or page.crawled == False:

        results = get_page(page.url)
        print('CRAWLING: ', page.url)
        print('CRAWLING STATUS: ', results[1])

        page_dict = {
            'raw_html': None,
            'status': 0,
            'content_type': None,
        }

        if results[0]:
            start_time_1 = time.time()
            resp = results[2]

            if 'html' in resp['content_type']:

                page_dict['raw_html'] = resp['raw'] 
                print('CRAWLING TYPE: ', resp['content_type'])

            page_dict['content_type'] = resp['content_type']

        page_dict['status'] = results[1]

        page_form = WebPageForm(data=page_dict, instance=page)
        if page_form.is_valid():
            page = page_form.save()
            print('## Saved Page')
        else:
            print('## Error saving page')


# client = MongoClient('mongodb://localhost:27017/')
# m_pages = client.crawler_dumps.pages

# @shared_task
# def crawler(page_id):
#     # Crawl URL
#     try:
#         page = WebPage.objects.get(id=page_id)
#     except WebPage.DoesNotExist:
#         raise
#     else:
#         results = get_page(page.url)
#         print('CRAWLING: ', page.url)
#         print('CRAWLING STATUS: ', results[1])
#         if results[0]:
#             start_time_1 = time.time()
#             resp = results[2]

#             i = 0
#             print('SAVING STEP 1')
#             out_pages_ids = list()
#             for out_link in resp['out_links']:
#                 print(i)
#                 # Create new page if outlink does not exist
#                 # Adds to crawler after save
#                 #try:
#                 out_page, created = WebPage.objects.only('id').get_or_create(url=out_link)
#                 #except IntegrityError:

#                 out_pages_ids.append(out_page.id)
#                 # add out links as in link to current page
#                 #out_page.in_links.add(page)
#                 i +=1

#             print('SAVING OUTLINKS')
#             page.out_links.add(*out_pages_ids)
#             print('SAVING STEP 2')
#             # Save raw html to MongoDB
#             m = hashlib.md5()
#             content = resp['raw'].encode('utf-8')
#             m.update(content)
#             page.content_hash = m.hexdigest()

#             page.status = results[1]
#             page.crawled = True
#             print('SAVING STEP 3')
#             page.crawler_ip = settings.EXTERNAL_IP
#             page.save()
#             print('Saved page meta data on db (%fs)' % time.time() - start_time_1)


#             start_time_2 = time.time()
#             page_raw = {
#                 'db_id': page.pk,
#                 'raw': resp['raw']
#             }

#             print('Saving raw html to mongoDB')
#             page_id = m_pages.insert_one(page_raw).inserted_id
#             print('Successfully inserted in mongodb (%f)' % time.time() - start_time_2)

#         else:
#             page.status = results[1]
#             page.crawled = False
#             page.save()




