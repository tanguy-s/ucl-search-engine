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
        pages = WebPage.objects.all().order_by('url_hash')
        last_seen = 0
        i = 0
        for page in pages:
            i += 1
            print('page: %d' % i)
            if page.url_hash == last_seen:
            	page.delete()
            else:
            	last_seen = page.url_hash

