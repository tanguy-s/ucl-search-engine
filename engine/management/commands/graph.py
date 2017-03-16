from django.core.management.base import BaseCommand, CommandError

from engine import webpages_graph

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
            webpages_graph.build_graph(new_graph=False)

        elif options['options'] == 'clear':
            print('Clear option selected')
            webpages_graph.build_graph(new_graph=True)

        elif options['options'] == 'pagerank':
            print('PageRank option selected')
            webpages_graph.get_pagerank('cs_ucl_graph.gpickle')


