import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from engine.models import WebPage
from engine.crawler import get_page
from engine.forms import WebPageForm
from engine.tasks import crawler_v2

import hashlib

class Command(BaseCommand):

    def handle(self, *args, **options):

        num_uncrawled = len(WebPage.objects.filter(url_hash=''))
        print('Uncrawled pages: %d' % num_uncrawled)
        pages = WebPage.objects.filter(url_hash='')

        i = 0
        for page in pages:
            i += 1
            print('page: %d' % i)
            page.save()

