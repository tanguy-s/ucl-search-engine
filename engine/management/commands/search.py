from django.core.management.base import BaseCommand, CommandError

from engine import query

class Command(BaseCommand):
    help = 'Type query to be searched'

    args = "[create_index, clear_index, index_pages]"


    def add_arguments(self, parser):
        parser.add_argument('--options', type=str)
        #parser.add_argument('-clear',default=False)


    def handle(self, *args, **options):
        print("Handling...")

        query.search()