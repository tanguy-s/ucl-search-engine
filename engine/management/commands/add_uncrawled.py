import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from engine.models import WebPage
from engine.crawler import get_page
from engine.forms import WebPageForm
from engine.tasks import crawler_v2

import hashlib

def simple_crawl(page):
    # Crawl URL
    #page, created = WebPage.objects.get_or_create(url=page_url)
    print('hello')
    print('URL', page.url)
    if page.crawled == False:

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
                    #simple_crawl(out_link)

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

    else:
    	print('already crawled')

class Command(BaseCommand):

    def handle(self, *args, **options):

        num_uncrawled = len(WebPage.objects.filter(status=0))
        print('Uncrawled pages: %d' % num_uncrawled)
        pages = WebPage.objects.filter(status=0)

        i = 0
        for page in pages:
            i += 1
            print('page: %d' % i)
            crawler_v2.delay(page.url)


#19:06 -> 41889 
