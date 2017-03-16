import time
import os, os.path
from whoosh import index
from engine.schema import MySchema
from engine.models import WebPage
from bs4 import BeautifulSoup
from whoosh import fields
from whoosh.fields import TEXT
import pickle


def getHeaders(soup, header):
    headers = soup.find_all(header)
    h_string = ""
    for h in headers:
        if h.text == '\n':
            continue
        h_string += h.text + '\n'
    return h_string

def getIndex(clearIndex):
    if clearIndex:
        input_var = input("Are you sure you want to clean index (yes|no): ")
        if input_var == 'yes':
            ix = index.create_in("indexdir", MySchema)
        else:
            exit(1)
    else:
        print('Getting index...')
        if not index.exists_in("indexdir"):
            print("Index does not exist in indexdir folder so new one was created")
            ix = index.create_in("indexdir", MySchema)
        else:
            ix = index.open_dir("indexdir")
    return ix


def updateRank():
    # get index
    ix = getIndex(False)

    # number of pages in database
    #num_pages = WebPage.objects.all().count()
    num_pages = WebPage.objects.only(*['url']).filter(crawled=True, status__startswith=2).count()
    print("Number of pages in database: {}".format(num_pages))

    # unserializing pagerank dictionary
    with open('cs_ucl_pagerank.pickle', 'rb') as pr_file:
        pr_dict = pickle.load(pr_file)

    # defining initial limiters of slice
    slice_size = 200
    start = 0
    end = start+slice_size
    num_pages_indexed = 0
    num_pages_not_crawled = 0
    num_pages_failed = 0
    num_ranks_failed = 0

    # while there is still pages to collect
    while start < num_pages:
        print("Start slice: {} - End slice: {}".format(start,end))
        pages = WebPage.objects.all()[start:end]

        for page in pages:

            try:
                rank = pr_dict[page.url]
            except KeyError:
                rank = 0
                file = open('failed_rank_pages.txt', 'a')
                file.write(page.url + '\n')
                file.close()
                num_ranks_failed += 1

            # update rank in index
            writer = ix.writer()


def indexPages(clearIndex):

    # get index
    ix = getIndex(clearIndex)

    # number of pages in database
    #num_pages = WebPage.objects.all().count()
    num_pages = WebPage.objects.only(*['url']).filter(indexed=False, status=200, content_type__contains='text/html').count()
    print("Number of pages in database: {}".format(num_pages))

    # unserializing pagerank dictionary
    with open('cs_ucl_pagerank.pickle', 'rb') as pr_file:
        pr_dict = pickle.load(pr_file)

    # defining initial limiters of slice
    slice_size = 2000
    start = 0
    end = start+slice_size

    num_pages_indexed = 0
    num_pages_not_crawled = 0
    num_pages_failed = 0
    num_ranks_failed = 0

    print('Optimizing..')
    writer = ix.writer()
    writer.commit(optimize=True)
    print('Done')

    
    fields = ['url', 'raw_html', 'created_at', 'updated_at']

    while start < num_pages:
        print("Start slice: {} - End slice: {}".format(start,end))
        start_time = time.time()
        pages = WebPage.objects.only(*fields).filter(indexed=False, status=200, content_type__contains='text/html')[start:end]
        print('Elapsed time for Query %.04f' % (time.time() - start_time))

        writer = ix.writer()

        indexed_ids = list()


        for page in pages:

            # Getting number of inlinks
            #in_links = page.in_links.count()

            # Parsing html with beautiful soup
            try:
                soup = BeautifulSoup(page.raw_html, 'html.parser')
            except:
                num_pages_failed += 1
                file = open('failed_pages.txt', 'w')
                file.write(page.url + '\n')
                file.close()
                continue

            # Getting title of webpage
            try:
                title = str(soup.title.string)
            except AttributeError:
                title = 'NA'

            # Getting headers
            h1 = getHeaders(soup, 'h1')
            h2 = getHeaders(soup, 'h2')
            h3 = getHeaders(soup, 'h3')
            h4 = getHeaders(soup, 'h4')
            #print('Elapsed time for BS4 %.04f' % (time.time() - start_time))

            # Getting content
            content = soup.get_text()
            
            try:
                rank = pr_dict[page.url]
            except KeyError:
                rank = 0
                file = open('failed_rank_pages.txt', 'a')
                file.write(page.url + '\n')
                file.close()
                num_ranks_failed += 1

            # Writing index to whoosh
            writer.add_document(url=page.url,
                                url_len=len(page.url),
                                url_txt=page.url,
                                date_updated=page.updated_at,
                                date_created=page.created_at,
                                content=content,
                                title_page=title,
                                h1=h1,
                                h2=h2,
                                h3=h3,
                                h4=h4,
                                rank=rank)

            # Setting index attribute to true in database
            #page.indexed = True
            #page.save()
            num_pages_indexed += 1
            indexed_ids.append(page.id)

            #print(page.url)

        print('Elapsed time for Fetching %.04f' % (time.time() - start_time))

        start_time_1 = time.time()
        print('Commiting ...')
        writer.commit()
        print('Elapsed time for commit %.04f' % (time.time() - start_time_1))

        print('Updating pages ...')
        WebPage.objects.filter(id__in=indexed_ids).update(indexed=True)

        print("{} pages indexed".format(num_pages_indexed))
        print("{} pages not crawled".format(num_pages_not_crawled))
        print("{} pages failed".format(num_pages_failed))
        print("{} ranks failed".format(num_ranks_failed))

        print('Total elapsed time %.04f\n' % (time.time() - start_time))

         # check if we have reached the end
        if end+slice_size > num_pages:
            slice_size = num_pages-end

        # update limiters of new slice
        start, end = end, end+slice_size


