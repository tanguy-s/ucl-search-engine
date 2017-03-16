from lxml import html

from django.core.management.base import BaseCommand, CommandError

from engine.models import WebPage
from engine.crawler import get_page_links

class Command(BaseCommand):

    def handle(self, *args, **options):

        pages = WebPage.objects.only(*['url', 'raw_html']).filter(
        	crawled=True, status__startswith=2)[0:50]
        print(len(pages))

        i = 0
        for page in pages:
            i += 1
            print('page: %d' % i)
            doc = html.fromstring(str.encode(page.raw_html))
            out_links = get_page_links(page.url, doc)
            print(out_links)


