import time
from django.core.management.base import BaseCommand, CommandError

from django.conf import settings
from django.db.models import Count

from engine.models import WebPage
import hashlib


class Command(BaseCommand):

    def handle(self, *args, **options):

        # total_links = len(WebPage.objects.only('id','url').all())
        # num_uncrawled = len(WebPage.objects.only('id','url').filter(status=0))
        # num_crawled = total_links - num_uncrawled

        # print('Main stats:')
        # print('[%d %d %d]' % (total_links, num_uncrawled, num_crawled))

        ctyp = '{'
        nums = list()
        
        num_html = len(WebPage.objects.only('id').filter(content_type__contains='text/html'))
        print('NUM HTML', num_html)
        results = WebPage.objects.values('content_type').annotate(num=Count('content_type')).order_by('-num')
        for res in results:
            ctyp += ", '%s'" % res['content_type']
            nums.append(res['num'])
        ctyp += '}'


        cstat = '{'
        nums = list()
        
        #num_html = len(WebPage.objects.only('id').filter(status='text/html'))
        #print('NUM HTML', num_html)
        num_2 = len(WebPage.objects.only('id').filter(status__startswith=2))
        num_4 = len(WebPage.objects.only('id').filter(status__startswith=4))
        num_5 = len(WebPage.objects.only('id').filter(status__startswith=5))
        print([num_2, num_4, num_5])
        results = WebPage.objects.values('status').annotate(num=Count('status')).order_by('-num')
        for res in results:
            cstat += ", '%s'" % res['status']
            nums.append(res['num'])
        cstat += '}'

        print(cstat)
        print(nums)

        #WebPage.objects.values('status').annotate(num=Count('status'))


#19:06 -> 41889 
