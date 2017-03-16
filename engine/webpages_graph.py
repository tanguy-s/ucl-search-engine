import networkx as nx
from engine.models import WebPage
import pickle
from engine.crawler import get_page_links
from lxml import html

def get_outlinks(page):
    try:
        doc = html.fromstring(str.encode(page.raw_html))
        return get_page_links(page.url, doc)
    except:
        return []

def add_nodes(ucl_graph):
    num_pages = WebPage.objects.only(*['url']).filter(crawled=True, status__startswith=2).count()

    # defining initial limiters of slice
    slice_size = 10000
    start = 0
    end = start+slice_size
    num_pages_added = 0

    # while there is still pages to collect
    while start < num_pages:
        print("Start slice: {} - End slice: {}".format(start,end))
        pages = WebPage.objects.only(*['url']).filter(crawled=True, status__startswith=2)[start:end]

        for page in pages:
            # add node if not already in graph
            if not ucl_graph.has_node(page.url):
                ucl_graph.add_node(page.url,out_links_processed=False)
                num_pages_added += 1

        # check if we have reached the end
        if end+slice_size > num_pages:
            slice_size = num_pages-end

        # update limiters of new slice
        start, end = end, end+slice_size

        print("{} pages added".format(num_pages_added))

    print("Finished adding nodes")
    return ucl_graph

def add_edges(ucl_graph):
    num_pages = WebPage.objects.only(*['url']).filter(crawled=True, status__startswith=2).count()

    # defining initial limiters of slice
    slice_size = 1000
    start = 0
    end = start+slice_size
    num_edges_added = 0
    num_pages_added = 0

    processed_outlinks = nx.get_node_attributes(ucl_graph, 'out_links_processed')

    # while there is still pages to collect
    while start < num_pages:
        print("Start slice: {} - End slice: {}".format(start,end))
        pages = WebPage.objects.only(*['url', 'raw_html']).filter(crawled=True, status__startswith=2)[start:end]

        for page in pages:
            #if processed_outlinks[page.url] == True:
            #    print('Hello')
            #    continue
            # add node if not already in graph
            if not ucl_graph.has_node(page.url):
                ucl_graph.add_node(page.url)
                num_pages_added += 1

            # add in-links: in-coming edges
            out_links = get_outlinks(page)
            for out_link in out_links:
                # add source of in-link to graph if not already added
                if not ucl_graph.has_node(out_link):
                    continue
                # add edge
                if ucl_graph.has_edge(page.url,out_link):
                    continue
                ucl_graph.add_edge(page.url,out_link)
                num_edges_added += 1

            # Setting attribute of processed_outlinks to true
            nx.set_node_attributes(ucl_graph, 'out_links_processed', {page.url : True})

        # check if we have reached the end
        if end+slice_size > num_pages:
            slice_size = num_pages-end

        # saving checkpoint of the graph in case it crashes
        if end % 10000 == 0:
            print("Saving graph...")
            nx.write_gpickle(ucl_graph, "cs_ucl_graph.gpickle")

        # update limiters of new slice
        start, end = end, end+slice_size

        print("{} edges added".format(num_edges_added))
        print("{} pages added".format(num_pages_added))

    print("Finished adding edges")
    return ucl_graph

def build_graph(new_graph):
    # number of pages in database
    num_pages = WebPage.objects.only(*['url', 'raw_html']).filter(crawled=True, status__startswith=2).count()
    print("Number of pages in database: {}".format(num_pages))

    if new_graph:
        # initializing directed graph:
        print("Creating new graph")
        ucl_graph = nx.DiGraph()
    else:
        # importing serialized graph
        print("Importing serialized graph")
        ucl_graph = nx.read_gpickle("cs_ucl_graph.gpickle")
        print("Current graph has {} nodes and {} edges".format(ucl_graph.number_of_nodes(), ucl_graph.number_of_edges()))

    # adding nodes
    ucl_graph = add_nodes(ucl_graph)

    nx.write_gpickle(ucl_graph, "cs_ucl_graph.gpickle")

    # adding edges
    ucl_graph = add_edges(ucl_graph)

    print("Saving graph...")
    nx.write_gpickle(ucl_graph, "cs_ucl_graph.gpickle")

    # calculating page rank
    get_pagerank("cs_ucl_graph.gpickle")

    print("Finished building graph")



def pagerank(G, alpha=0.85, max_iter=100):
    # Create a copy in (right) stochastic form
    graph_copy = G
    W = nx.stochastic_graph(graph_copy, weight='weight')
    num_nodes = W.number_of_nodes()

    # initializing uniform starting vector
    x = dict.fromkeys(W, 1.0 / num_nodes)

    # Using also uniform distribution for the weights of "dead end" nodes
    dead_ends = [n for n in W if W.out_degree(n, weight='weight') == 0.0]

    # power iteration: make up to max_iter iterations
    for i in range(max_iter):
        # storing result of last iteration to be able to check for convergence
        xlast = x

        # begin new iteration of algorithm
        x = dict.fromkeys(xlast.keys(), 0)
        dead_ends_sum = alpha * sum(xlast[n] for n in dead_ends)
        for n in x:
            # x^T=xlast^T*W
            for nbr in W[n]:
                x[nbr] += alpha * xlast[n] * W[n][nbr]['weight']

            # calculate transition matrix that represents the markov chain
            # used in Google's PageRank algorithm (teleporting):
            x[n] += dead_ends_sum * (1.0 / num_nodes) + (1.0 - alpha) * (1.0 / num_nodes)

        # check for convergence (l1 norm)
        err = sum([abs(x[n] - xlast[n]) for n in x])
        tol = 1.0e-6
        if err < num_nodes*tol:
            print('PageRank algorithm converged in {} iterations'.format(i))
            return x

    print('PageRank algorithm did not converge in {} maximum iterations'.format(max_iter))


def get_pagerank(graph_filename):
    # importing serialized graph
    ucl_graph = nx.read_gpickle(graph_filename)

    # calling networkx pagerank function using default value of 0.85 for alpha (damping parameter)
    print("Calculating pagerank for all nodes")
    pr = pagerank(ucl_graph)
    print("Finished calculating page rank")

    # serializing pagerank dictionary
    with open('pagerank.pickle', 'wb') as pr_file:
        pickle.dump(pr,pr_file)

    return pr