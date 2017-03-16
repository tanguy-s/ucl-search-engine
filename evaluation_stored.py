from engine.query import search
from test_data import util
from math import log
import pickle
import json


def store_res(k, search_type, incorporate_pr):
    queries = ['Computer Science','Computer','Computer Room','Computer Science Department','Jun Wang',
               'Emine Yilmaz','Machine Learning', 'Web Science and Big Data Analytics',
               'Data Science', 'Information Retrieval and Data Mining', 'Web Economics', 'Supervised Learning',
               'Applied Machine Learning', 'Statistical Natural Language Processing', 'Sebastian Riedel',
               'MsC Computer Science', 'Research', 'Computer Science Research', 'Admissions', 'Computer Science BsC'
               'Advanced Topics in Machine Learning', 'Deep Mind', 'Google', 'Thesis', 'Thesis Projects',
               'Courses', 'Fees', 'Mark Herbster', 'David Barber', 'computer science phd', 'research projects',
               'Computer science department', 'Machine Learning Syllabus', 'Deep Learning', 'Computer Science courses',
               'Timetable', 'Exams', 'Exam timetable', 'Computer Science facilities', 'Computer hub', 'Underground station',
               'Microsoft Research', 'Euston Square', 'London East Campus', 'Roberts Engineering Building',
               'Main Quad', 'Twitter Botnets', 'Starcraft playing AI', 'AlphaGo', 'Philip Treleaven', 'Bloomsbury',
               'Phineas', 'Weekend activities', 'Computer Science Staff', 'Mathematics Staff', 'Financial Computation',
               'regression trees', 'Distribute Systems and Security', 'DSS', 'Brad Karp', 'Stanford', 'Airports',
               'traffic control', 'Self driving cars', 'Uber', 'Insurance', 'Risk prediction', 'Bursary', 'Grants',
               'Library', 'Group study rooms', 'moodle', 'portico', 'Tottenham Court Road', 'Holborn', 'Growing Trees',
               'Adaboost', 'UCL staff', 'password reset', 'The art of generating a test set']

    res = {}
    for query in queries:
        res[query] = [search(query, search_type, operation_type='and', type_input=False, incorporate_pr=incorporate_pr, verbose=False, num_results=k)]

    # serializing results dictionary
    file_name = 'query_res_' + search_type + '_pr_' + incorporate_pr + '_10' + '.pickle'
    with open(file_name, 'wb') as res_file:
        pickle.dump(res,res_file)


def store_all_queries(k):

    print('Storing all queries for all algorithms')

    search_algorithms = ['bm25', 'tfidf', 'both']
    pr_options = ['yes', 'no']

    for algorithm in search_algorithms:
        for option in pr_options:
            store_res(k, search_type=algorithm, incorporate_pr=option)
            print_string = 'Done storing all query results for algorithm: ' + algorithm + ' and PageRank: ' + option
            print(print_string)

    print('Done storing all results')

def precision_at_k(k, query, retrieved, test_set, num_relevant=100):

    # getting relevant documents
    if test_set == 'google':
        with open('google_results.json') as res_google:
            google_dict = json.load(res_google)
            relevant = google_dict[query]
    elif test_set == 'ucl':
        relevant = util.get_nbest_results(query,num_relevant)
    else:
        print('Not a valid dataset')
        exit(1)

    print("{} relevant documents obtained".format(len(relevant)))

    # getting number of relevant documents that were retrieved
    relevant_retrieved_docs = [doc for doc in retrieved if doc in relevant]
    #print(relevant_retrieved_docs)
    num_relevant_retrieved = len(relevant_retrieved_docs)
    #print("{} relevant documents retrieved".format(num_relevant_retrieved))

    return num_relevant_retrieved / k, len(relevant)


def calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant):

    opt_dcg = 0

    # return -1 in case there are 0 retrieved documents, so that we do not divide by 0
    if num_retrieved == 0:
        return -1

    for i in range(num_retrieved):
        rank = i+1
        # in best case, all retrieved documents are highly relevant
        if num_highly_relevant > 0:
            rel_i = 2
            num_highly_relevant -= 1
        # in case we have run out of highly relevant documents then it can only be relevant from now on
        elif num_relevant > 0:
            rel_i = 1
            num_relevant -= 1
        # in case we have run out of relevant documents as well, then they are not relevant
        else:
            rel_i = 0

        # calculate discount based on rank of document (same as before)
        if rank == 1:
            discount = 1
        else:
            discount = log(rank,2)

        # add discounted gain to DCG value (same as before)
        opt_dcg += rel_i / discount

    return opt_dcg



def ndcg(query, retrieved, test_set, num_relevant=100):

    # getting relevant documents
    if test_set == 'google':
        with open('google_results.json') as res_google:
            google_dict = json.load(res_google)
            relevant = google_dict[query]
    elif test_set == 'ucl':
        relevant = util.get_nbest_results(query,num_relevant)
    else:
        print('Not a valid dataset')
        exit(1)

    print("{} relevant documents obtained".format(len(relevant)))

    # defining the first 10 documents as highly relevant
    # (relvance 2), the remaining documents as relevant (relevance 1)
    # and all the rest are deemed irrelevant (relevance 0)
    # these values might have to be changed approprietely
    num_highly_relevant = 10
    num_relevant = num_relevant - 10

    highly_relevant = relevant[:num_highly_relevant]
    relevant = relevant[num_highly_relevant:]

    dcg = 0
    rank = 1
    for doc in retrieved:
        # find relevance of retrieved doc
        if doc in highly_relevant:
            rel_doc = 2
        elif doc in relevant:
            rel_doc = 1
        else:
            rel_doc = 0

        # calculate discount based on rank of document
        if rank == 1:
            discount = 1
        else:
            discount = log(rank,2)

        # add discounted gain to DCG value
        dcg += rel_doc / discount

        # update rank
        rank += 1

    # find number of retrieved documents by finding length of list (since it might be smaller than k)
    num_retrieved = len(retrieved)
    opt_dcg = calc_optimal_dcg(num_retrieved,num_highly_relevant,num_relevant)

    # divide by optimal value to get normalized DCG
    ndcg = dcg / opt_dcg

    return ndcg, len(relevant)


def calc_res(res, metric):

    times_res = [res[key][1] for key in res]

    if metric == 'precision':
        eval_res = [res[key][0] for key in res]
        eval_res_with_rel_docs = [res[key][0] for key in res if res[key][2] >= 5 and res[key][0] != 0]
    elif metric == 'ndcg':
        eval_res = [res[key][0] for key in res if res[key][0] >= 0]
        eval_res_with_rel_docs = [res[key][0] for key in res if res[key][2] > 0 and res[key][0] >= 0]

    print("Average of evaluation metrics: {}".format(sum(eval_res)/len(eval_res)))
    print("Average of run times: {} seconds".format(sum(times_res) / len(times_res)))
    if metric == 'precision':
        print("Average of evaluation metrics for queries with at least 5 relevant documents: {}".format(sum(eval_res_with_rel_docs) / len(eval_res_with_rel_docs)))
    elif metric == 'ndcg':
        print("Average of evaluation metrics for queries with more than 0 retrieved and relevant documents: {}".format(sum(eval_res_with_rel_docs) / len(eval_res_with_rel_docs)))



def calc_metrics(num_relevant, test_set, metric):

    print('Calculating evaluation metrics from stored queries')

    search_algorithms = ['bm25', 'tfidf', 'both']
    pr_options = ['yes', 'no']

    #search_algorithms = ['both']
    #pr_options = ['yes','no']

    for algorithm in search_algorithms:
        for option in pr_options:
            # initializing empty res dict
            metrics_res = {}

            # unserializing file
            file_name = 'query_res_' + algorithm + '_pr_' + option + '.pickle'
            with open(file_name, 'rb') as res_file:
                queries_dict = pickle.load(res_file)
                for query, res in queries_dict.items():
                    # getting precision resutls
                    if metric == 'precision':
                        if len(res[0][0]) != 0:
                            metric_val, actual_num_relevant = precision_at_k(k=len(res[0][0]), query=query, retrieved=res[0][0], test_set=test_set, num_relevant=num_relevant)
                        #metric_val, actual_num_relevant = precision_at_k(k=5, query=query, retrieved=res[0][0], test_set=test_set, num_relevant=num_relevant)
                    else:
                        metric_val, actual_num_relevant = ndcg(query=query, retrieved=res[0][0], test_set=test_set, num_relevant=num_relevant)

                    # storing in dict -> query : [metric_value runtime, num_relevant]
                    metrics_res[query] = [metric_val, res[0][1], actual_num_relevant]

                # calculating averages
                print_string = 'Metric results for all queries for algorithm: ' + algorithm + ' and PageRank: ' + option + ' and metric: ' + metric + ':'
                print(print_string)
                calc_res(metrics_res, metric=metric)

    print('Done calculating and storing all results')


calc_metrics(num_relevant=100, test_set='google', metric='ndcg')
