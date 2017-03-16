from whoosh import index
from whoosh import qparser
from whoosh.qparser import QueryParser
from whoosh.scoring import TF_IDF, BM25F
from whoosh import highlight
from whoosh.qparser.dateparse import DateParserPlugin
import engine.utils as utils


def getIndex():
    if not index.exists_in("indexdir"):
        print("Index does not exist in indexdir folder")
        exit(1)
    else:
        ix = index.open_dir("indexdir")
    return ix


def combine_pagerank(results):

    if len(results) > 0:
        max_score = max([r.score for r in results])
        max_rank = max([r.fields()["rank"] for r in results])

        combined = []
        for r in results:
            fields = r.fields()
            # normalizing score and rank so both have moreless same weight when added
            r.score = r.score/max_score
            r.rank = fields["rank"]/max_rank
            r.combined = r.score + r.rank
            combined.append(r)

        combined.sort(key=lambda x: x.combined, reverse=True)
    else:
        combined = []

    return combined


def searcher(ix, query, w):
    searcher = ix.searcher(weighting=w)
    results = searcher.search(query, limit=None)
    results.fragmenter = highlight.ContextFragmenter(maxchars=50, surround=50, )
    return results, results.scored_length(), results.runtime, searcher


def combine_res(res1,res2):
    if len(res1) == 0 and len(res2) == 0:
        return []

    max_score1 = max([r.score for r in res1])
    max_score2 = max([r.score for r in res2])

    # normalizing scores of both models
    for r in res1:
        r.score = r.score / max_score1
    for r in res2:
        r.score = r.score / max_score2

    res1 = [e for e in res1]
    res1.sort(key=lambda x: x.rank, reverse=True)
    res1 = res1[:500]

    res2 = [e for e in res2]
    res2.sort(key=lambda x: x.rank, reverse=True)
    res2 = res2[:500]

    combined = []
    for r1 in res1:
        url_1 = r1.fields()['url']
        for r2 in res2:
            url_2 = r2.fields()['url']
            if url_1 == url_2:
                r1.score += r2.score
                combined.append(r1)
                break

    combined.sort(key=lambda x: x.score, reverse=True)
    print("{} results for combined search".format(len(combined)))

    return combined




def search(query='', search_type='', operation_type='', type_input=True, incorporate_pr=True, verbose=True, num_results=10):

    # getting index
    ix = getIndex()

    if type_input:
        query = input("Type here what you would like to search: ")
        search_type = input("What weighting algorithm would you like to test? ")
        operation_type = input("What operation would you like? (AND | OR): ")
        incorporate_pr = input("Would you like to incorporate pagerank in your search? (yes | no): ")

    if search_type.lower() == "bm25":
        w = BM25F(B=0.75, K1=1.5)
    elif search_type.lower() == "tfidf":
        w = TF_IDF()
    elif search_type.lower() == "both":
        w = TF_IDF()
    else:
        print("That is not a valid algorithm")
        exit(1)

    if operation_type.lower() == "and":
        op_type = qparser.AndGroup
    elif operation_type.lower() == "or":
        op_type = qparser.AndGroup
    else:
        print("That is not a valid operation")
        exit(1)

    fields = ['url', 'url_txt', 'url_len', 'date_created', 'date_updated', 'content', 'title_page', 'h1', 'h2', 'h3', 'h4', 'rank']

    # Parsing inputted query:
    qp = qparser.MultifieldParser(fields, ix.schema, group=op_type)

    # adding plugins
    qp.add_plugin(qparser.PlusMinusPlugin)
    qp.add_plugin(DateParserPlugin)
    qp.add_plugin(qparser.FuzzyTermPlugin)

    # Parsing query
    query = qp.parse(query)

    # Perform search
    results, found_doc_num, run_time, searcher1 = searcher(ix, query, w)

    if found_doc_num == 0:
        final_top_output = "Sorry " + str(found_doc_num) + " Search Results Found.\n" + "Search Results for " + \
                           str(query) + " using " + search_type + " (" + str(run_time) + " seconds)\n"

    else:
        final_top_output = "Top " + str(found_doc_num) + " Search Results\n" + "Search Results for " \
                           + str(query) + " using " + search_type + " (" + str(run_time) + " seconds)\n"

    if verbose:
        print(final_top_output)

    # second search if combined model option was chosen
    if search_type.lower() == 'both':
        results2, found_doc_num2, run_time2, searcher2 = searcher(ix, query, BM25F(B=0.75, K1=1.5))
        print("Done with second search")
        results = combine_res(results,results2)
        searcher2.close()

    # incorporating pagerank if chosen
    if incorporate_pr.lower() == 'yes':
        results = combine_pagerank(results)
    else:
        results = [e for e in results]
        results.sort(key=lambda x: x.rank, reverse=True)

    # print results
    res_urls = []
    if results:
        results = results[:num_results]
        for hit in results:
            snip = hit.highlights('title_page', top=2)
            url = hit['url']
            score = hit.score
            if verbose:
                print(str(url.encode('utf-8')), '\n', str(score), '\n', snip, "\n")
            res_urls.append(utils.get_redirected_link(url))

    # closing searcher
    searcher1.close()

    return res_urls, run_time