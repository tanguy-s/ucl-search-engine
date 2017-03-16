from django.core.management.base import BaseCommand, CommandError

from engine import index

class Command(BaseCommand):
    help = 'Indexing of webpages in whoosh'

    args = "[create_index, clear_index, index_pages]"


    def add_arguments(self, parser):
        parser.add_argument('--options', type=str)
        #parser.add_argument('-clear',default=False)


    def handle(self, *args, **options):
        print("Handling...")

        if options['options'] == 'update':
            print('Update option selected')
            index.indexPages(clearIndex=False)

        elif options['options'] == 'clear':
            print('Clear option selected')
            index.indexPages(clearIndex=True)


